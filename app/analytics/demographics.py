import hashlib
import logging
import os
import re
from collections import defaultdict
import pandas as pd
from app.database.postgres import get_db_connection

logger = logging.getLogger("demographics_engine")
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ============================================================
# 1. TAXONOMIES & KEYWORDS
# ============================================================

PROFESSIONS = {
    "student": [
        "student", "college", "university", "btech", "mtech", "degree",
        "jee", "neet", "upsc", "gpsc", "ssc", "exam", "aspirant", "study", "campus"
    ],
    "tech_professional": [
        "developer", "engineer", "software", "coder", "programmer",
        "python", "java", "javascript", "golang", "data scientist",
        "machine learning", "ai", "cyber security", "web developer", "devops"
    ],
    "trader_finance": [
        "trader", "trading", "crypto", "bitcoin", "investor", "investment",
        "stocks", "nifty", "banknifty", "options", "forex", "share market"
    ],
    "business_founder": [
        "founder", "ceo", "startup", "entrepreneur", "business", "owner", "agency"
    ],
    "educator": [
        "teacher", "professor", "lecturer", "faculty", "educator", "tutor", "mentor"
    ]
}

LOCATIONS = {
    "ahmedabad": ["ahmedabad", "amdavad", "gujarat"],
    "mumbai": ["mumbai", "bombay", "maharashtra"],
    "delhi_ncr": ["delhi", "new delhi", "noida", "gurgaon", "gurugram"],
    "bangalore": ["bangalore", "bengaluru", "karnataka"],
    "pune": ["pune"],
    "hyderabad": ["hyderabad", "telangana"],
    "chennai": ["chennai", "madras", "tamil nadu"],
    "kolkata": ["kolkata", "calcutta", "west bengal"],
    "surat": ["surat"],
    "vadodara": ["vadodara", "baroda"],
    "pan_india": ["india", "bharat", "hindustan"]
}

INTERESTS = {
    "technology": ["python", "coding", "programming", "ai", "ml", "software", "tech", "web3"],
    "finance_markets": ["stock", "trading", "crypto", "bitcoin", "nifty", "sensex", "mutual fund"],
    "competitive_exams": ["study", "exam", "jee", "neet", "upsc", "prelims", "syllabus"],
    "sports": ["cricket", "football", "fifa", "ipl", "virat", "rohit", "badminton"],
    "entertainment": ["movie", "movies", "music", "bollywood", "netflix", "series", "gaming"]
}

AGE_PATTERNS = [
    (r"\b(\d{1,2})\s*(?:years old|yrs old|year old|yo)\b"),
    (r"\bage\s*[:=-]?\s*(\d{1,2})\b"),
    (r"\bi.?m\s*(\d{1,2})\b")
]

# ============================================================
# 2. INFERENCE HELPERS
# ============================================================

def anonymize_id(raw_id: str) -> str:
    """Generates an irreversible pseudonymized ID for SIH compliance."""
    return "anon_" + hashlib.sha256(str(raw_id).encode("utf-8")).hexdigest()[:12]

def get_age_group(age: int) -> str:
    if age is None:
        return "unknown"
    if age < 18:
        return "under_18"
    if age <= 24:
        return "18-24"
    if age <= 34:
        return "25-34"
    if age <= 44:
        return "35-44"
    return "45+"

def infer_age(text: str):
    if not text:
        return None, "unknown"
    text_lower = text.lower()
    for pattern in AGE_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            try:
                age = int(match.group(1))
                if 13 <= age <= 90:
                    return age, get_age_group(age)
            except ValueError:
                pass
    return None, "unknown"

def infer_taxonomy(text: str, taxonomy_dict: dict) -> list:
    if not text:
        return []
    text_lower = text.lower()
    detected = []
    for category, keywords in taxonomy_dict.items():
        for kw in keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text_lower):
                detected.append(category)
                break
    return detected

# ============================================================
# 3. ANALYSIS AND AGGREGATION PIPELINE
# ============================================================

def run_demographics_pipeline():
    """
    1. Fetches user metadata & aggregated message context.
    2. Infers demographics using privacy-safe techniques.
    3. Persists aggregate segments into PostgreSQL.
    4. Writes sanitized CSV files for dashboard presentation.
    """
    # Joins user bio and sample message activity per channel to maximize signal
    query = """
        SELECT 
            u.user_id,
            COALESCE(u.bio, '') AS bio,
            COALESCE(u.username, '') AS username,
            COALESCE(u.language_code, 'en') AS language,
            m.channel_id,
            STRING_AGG(SUBSTRING(m.text FROM 1 FOR 100), ' ') AS message_sample
        FROM users u
        JOIN messages m ON u.user_id = m.user_id
        GROUP BY u.user_id, u.bio, u.username, u.language_code, m.channel_id;
    """

    with get_db_connection() as conn:
        df_raw = pd.read_sql_query(query, conn)

    if df_raw.empty:
        logger.warning("No user data found to analyze.")
        return

    anonymized_user_records = []
    # Key: (channel_id, segment_type, segment_name) -> count
    channel_aggregates = defaultdict(int)

    for _, row in df_raw.iterrows():
        combined_text = f"{row['bio']} {row['username']} {row['message_sample'] or ''}"
        
        age, age_group = infer_age(combined_text)
        professions = infer_taxonomy(combined_text, PROFESSIONS) or ["unspecified"]
        locations = infer_taxonomy(combined_text, LOCATIONS) or ["unspecified"]
        interests = infer_taxonomy(combined_text, INTERESTS) or ["general"]
        channel = str(row["channel_id"])

        # Update aggregates
        channel_aggregates[(channel, "age_group", age_group)] += 1
        for p in professions:
            channel_aggregates[(channel, "profession", p)] += 1
        for l in locations:
            channel_aggregates[(channel, "location", l)] += 1
        for item in interests:
            channel_aggregates[(channel, "interest", item)] += 1

        # Build individual anonymized record (no usernames, bios, or raw user IDs)
        anonymized_user_records.append({
            "anonymous_id": anonymize_id(row["user_id"]),
            "channel_id": channel,
            "language": row["language"],
            "age_group": age_group,
            "primary_profession": professions[0],
            "primary_location": locations[0],
            "primary_interest": interests[0]
        })

    # Prepare DataFrames
    df_users_anonymized = pd.DataFrame(anonymized_user_records)

    aggregate_rows = [
        {
            "channel_id": k[0],
            "segment_type": k[1],
            "segment_name": k[2],
            "user_count": v
        }
        for k, v in channel_aggregates.items()
    ]
    df_aggregates = pd.DataFrame(aggregate_rows)

    # Calculate segment percentage distribution per channel & segment type
    df_aggregates["total_in_type"] = df_aggregates.groupby(["channel_id", "segment_type"])["user_count"].transform("sum")
    df_aggregates["percentage"] = (df_aggregates["user_count"] / df_aggregates["total_in_type"] * 100).round(2)
    df_aggregates.drop(columns=["total_in_type"], inplace=True)

    # Persist Aggregates to PostgreSQL
    upsert_query = """
        INSERT INTO demographic_aggregates (channel_id, segment_type, segment_name, user_count, last_updated)
        VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (channel_id, segment_type, segment_name)
        DO UPDATE SET user_count = EXCLUDED.user_count, last_updated = CURRENT_TIMESTAMP;
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            records_to_insert = [
                (r["channel_id"], r["segment_type"], r["segment_name"], int(r["user_count"]))
                for _, r in df_aggregates.iterrows()
            ]
            cur.executemany(upsert_query, records_to_insert)
            conn.commit()

    logger.info(f"Updated {len(records_to_insert)} demographic segment rows in PostgreSQL.")

    # ============================================================
    # 4. SILENT CSV EXPORTS (DATA DIRECTORY)
    # ============================================================
    os.makedirs("data", exist_ok=True)
    
    summary_csv = "data/demographics_channel_summary.csv"
    anon_csv = "data/demographics_anonymized_segments.csv"

    df_aggregates.sort_values(by=["channel_id", "segment_type", "user_count"], ascending=[True, True, False]).to_csv(summary_csv, index=False)
    df_users_anonymized.to_csv(anon_csv, index=False)

    logger.info(f"Successfully exported channel demographic summaries to: {summary_csv}")
    logger.info(f"Successfully exported anonymized segment dataset to: {anon_csv}")

if __name__ == "__main__":
    run_demographics_pipeline()