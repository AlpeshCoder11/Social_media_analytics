import os
import re
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Automatically resolve project root
sys.path.append(str(Path(__file__).resolve().parents[2]))

try:
    from app.database.postgres import get_db_connection
except ImportError:
    get_db_connection = None

logger = logging.getLogger("trend_engine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ============================================================
# 1. NOISE & STOPWORDS FILTER (EMBEDDED FOR PORTABILITY)
# ============================================================
try:
    from app.analytics.noise_words import NOISE_WORDS
    logger.info(f"Loaded {len(NOISE_WORDS)} custom multilingual noise words.")
except ImportError:
    logger.warning("Custom noise_words.py not found. Falling back to basic filter.")
    NOISE_WORDS = {"the", "and", "is", "hai", "bhai"} # Basic fallback
# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================
def clean_text_for_trends(text: str) -> str:
    """Cleans text while preserving hashtags and valid alphanumeric words."""
    if not text:
        return ""
    text = str(text).lower()
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#(\w+)", r" \1 ", text)  # Keep hashtag content
    text = re.sub(r"\b\d+(?:[./:-]\d+)*\b", " ", text)  # Strip standalone dates/numbers
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    tokens = [
        token for token in text.split()
        if token not in NOISE_WORDS
        and len(token) >= 3
        and not token.isdigit()
    ]
    return " ".join(tokens)

# ============================================================
# 3. DATA LOADER (POSTGRESQL WITH CSV FALLBACK)
# ============================================================
def load_dataset():
    """Fetches messages and sentiment from PostgreSQL, falls back to CSV if offline."""
    df = pd.DataFrame()
    
    if get_db_connection:
        try:
            query = """
                SELECT 
                    m.message_id,
                    m.channel_id,
                    m.timestamp AS date,
                    m.text,
                    COALESCE(s.label, 'neutral') AS sentiment_label,
                    COALESCE(s.score, 0.0) AS sentiment_score
                FROM messages m
                LEFT JOIN sentiment_results s ON m.message_id = s.message_id
                WHERE m.text IS NOT NULL AND TRIM(m.text) != ''
                ORDER BY m.timestamp ASC;
            """
            with get_db_connection() as conn:
                df = pd.read_sql_query(query, conn)
            logger.info(f"Loaded {len(df)} records directly from PostgreSQL.")
        except Exception as e:
            logger.warning(f"PostgreSQL connection failed ({e}). Attempting local CSV fallback...")

    if df.empty:
        for csv_path in ["data/sentiment_results.csv", "telegram_data.csv"]:
            if os.path.exists(csv_path):
                df = pd.read_csv(csv_path)
                logger.info(f"Loaded {len(df)} records from {csv_path}.")
                break

    if df.empty:
        raise ValueError("No data found in PostgreSQL or local CSV files.")

    # Harmonize date and text columns
    date_col = "date" if "date" in df.columns else "timestamp"
    df["date"] = pd.to_datetime(df[date_col], errors="coerce")
    df["text"] = df["text"].fillna("").astype(str)
    df = df.dropna(subset=["date"]).copy()
    df["clean_text"] = df["text"].apply(clean_text_for_trends)
    df = df[df["clean_text"].str.strip() != ""].copy()
    df = df.sort_values("date").reset_index(drop=True)

    # Engagement scoring (views, forwards, replies if available)
    views = pd.to_numeric(df["views"], errors="coerce").fillna(0) if "views" in df.columns else 0.0
    forwards = pd.to_numeric(df["forwards"], errors="coerce").fillna(0) if "forwards" in df.columns else 0.0
    replies = pd.to_numeric(df["replies"], errors="coerce").fillna(0) if "replies" in df.columns else 0.0
    
    df["engagement"] = 1.0 + np.log1p(views) + 2.0 * np.log1p(forwards) + 1.5 * np.log1p(replies)

    return df

# ============================================================
# 4. HIGH-SPEED VECTORIZED TREND ENGINE
# ============================================================
def extract_ngram_counts(df_subset, min_gram=1, max_gram=3):
    """
    Extracts phrase counts and maps which messages match each topic
    in O(N) time without nested regex string matching.
    """
    phrase_counts = Counter()
    phrase_engagement = defaultdict(float)
    phrase_sentiment = defaultdict(list)

    for idx, row in df_subset.iterrows():
        words = row["clean_text"].split()
        doc_phrases = set()

        # Generate 1-gram, 2-gram, and 3-grams
        for n in range(min_gram, max_gram + 1):
            for i in range(len(words) - n + 1):
                ngram = " ".join(words[i:i + n])
                if not any(w in NOISE_WORDS for w in ngram.split()):
                    doc_phrases.add(ngram)

        for phrase in doc_phrases:
            phrase_counts[phrase] += 1
            phrase_engagement[phrase] += row["engagement"]
            if "sentiment_label" in row and pd.notna(row["sentiment_label"]):
                phrase_sentiment[phrase].append(row["sentiment_label"])

    return phrase_counts, phrase_engagement, phrase_sentiment

def compute_trends():
    df = load_dataset()

    if len(df) < 5:
        logger.warning("Insufficient messages to execute trend detection.")
        return pd.DataFrame()

    # Time Window Partitioning
    max_date = df["date"].max()
    min_date = df["date"].min()
    data_days = max(1, (max_date - min_date).total_seconds() / 86400)

    if data_days >= 7:
        window_days = 3
    else:
        window_days = max(1, data_days / 2)

    recent_cutoff = max_date - pd.Timedelta(days=window_days)
    previous_cutoff = recent_cutoff - pd.Timedelta(days=window_days)

    recent_df = df[df["date"] >= recent_cutoff].copy()
    previous_df = df[(df["date"] >= previous_cutoff) & (df["date"] < recent_cutoff)].copy()

    # Fallback to 50/50 temporal split if previous window has no data
    if previous_df.empty:
        split_idx = len(df) // 2
        previous_df = df.iloc[:split_idx].copy()
        recent_df = df.iloc[split_idx:].copy()

    logger.info(f"Analyzing {len(recent_df)} recent messages vs {len(previous_df)} baseline messages.")

    # Fast Count Extraction
    recent_counts, recent_eng, recent_sent = extract_ngram_counts(recent_df)
    prev_counts, _, _ = extract_ngram_counts(previous_df)

    results = []
    # Evaluate topics that appear at least 2 times recently
    for topic, r_count in recent_counts.items():
        if r_count < 2:
            continue

        words = topic.split()
        p_count = prev_counts.get(topic, 0)

        # Growth / Velocity
        if p_count == 0:
            growth_pct = 100.0
            growth_factor = "NEW"
        else:
            growth_pct = ((r_count - p_count) / p_count) * 100.0
            growth_factor = f"{(r_count / p_count):.2f}x"

        velocity = r_count / max(window_days, 1)
        eng_score = np.log1p(recent_eng[topic])
        phrase_bonus = 1.0 + (0.25 * (len(words) - 1))
        capped_growth = min(max(growth_pct, 0), 500)

        # Formula matches the architecture's momentum model
        momentum_score = r_count * (1 + capped_growth / 100) * (1 + eng_score / 10) * phrase_bonus

        # Trend Status
        if p_count == 0 and r_count >= 3:
            status = "BREAKING_NEW"
        elif growth_pct >= 100:
            status = "SURGING"
        elif growth_pct >= 30:
            status = "RISING"
        elif growth_pct <= -40:
            status = "FADING"
        else:
            status = "STEADY"

        # Dominated Sentiment Mode for this Trend
        sentiments = recent_sent.get(topic, [])
        top_sentiment = Counter(sentiments).most_common(1)[0][0] if sentiments else "neutral"

        results.append({
            "topic": topic,
            "recent_mentions": r_count,
            "previous_mentions": p_count,
            "growth_percent": round(growth_pct, 1),
            "growth_factor": growth_factor,
            "dominant_sentiment": top_sentiment,
            "recent_engagement": round(recent_eng[topic], 2),
            "velocity_per_day": round(velocity, 2),
            "momentum_score": round(momentum_score, 2),
            "status": status
        })

    trend_df = pd.DataFrame(results)

    if trend_df.empty:
        logger.warning("No emerging trends found.")
        return trend_df

    # Sort and eliminate substrings if a more informative multi-word phrase exists
    trend_df = trend_df.sort_values("momentum_score", ascending=False).reset_index(drop=True)
    trend_df = trend_df.head(100)

    return trend_df

# ============================================================
# 5. PERSISTENCE & CSV EXPORT
# ============================================================
def save_trends(trend_df: pd.DataFrame):
    if trend_df.empty:
        return

    # 1. Export CSV
    os.makedirs("data", exist_ok=True)
    csv_path = "data/trend_results.csv"
    trend_df.to_csv(csv_path, index=False, encoding="utf-8")
    logger.info(f"Trend results saved to: {csv_path}")

    # 2. Persist to PostgreSQL (if accessible)
    if get_db_connection:
        try:
            upsert_query = """
                INSERT INTO trend_results (channel_id, topic, current_volume, previous_volume, growth_rate, trend_type, time_window, detected_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (channel_id, topic, time_window)
                DO UPDATE SET 
                    current_volume = EXCLUDED.current_volume,
                    previous_volume = EXCLUDED.previous_volume,
                    growth_rate = EXCLUDED.growth_rate,
                    trend_type = EXCLUDED.trend_type,
                    detected_at = CURRENT_TIMESTAMP;
            """
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    records = [
                        ("global_network", r["topic"], int(r["recent_mentions"]), int(r["previous_mentions"]),
                         float(r["growth_percent"]), r["status"], "72h")
                        for _, r in trend_df.iterrows()
                    ]
                    cur.executemany(upsert_query, records)
                    conn.commit()
            logger.info(f"Persisted {len(records)} trend topics to PostgreSQL trend_results table.")
        except Exception as e:
            logger.warning(f"Could not persist to PostgreSQL: {e}")

    # Console Summary
    print("\n" + "=" * 95)
    print("           SIH SOCIAL MEDIA ANALYTICS — ADVANCED TREND INTELLIGENCE")
    print("=" * 95)
    cols = ["topic", "recent_mentions", "growth_percent", "dominant_sentiment", "momentum_score", "status"]
    print(trend_df[cols].head(15).to_string(index=False))
    print("=" * 95 + "\n")

if __name__ == "__main__":
    df_trends = compute_trends()
    save_trends(df_trends)