import logging
import torch
from langdetect import detect
from transformers import pipeline
from app.database.postgres import get_db_connection
import csv
import os
import sys
from pathlib import Path

# Automatically add the project root (scocial_media_analytics) to Python's lookup path
sys.path.append(str(Path(__file__).resolve().parents[2]))

logger = logging.getLogger("sentiment_engine")
logging.basicConfig(level=logging.INFO)

# 1. Device and Precision Configuration
DEVICE = 0 if torch.cuda.is_available() else -1
TORCH_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32

logger.info(f"Initializing Sentiment Tri-Pipeline on device: {'cuda:0 (RTX 3050)' if DEVICE == 0 else 'CPU'}")

# 2. Load Models onto GPU
eng_analyzer = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
    device=DEVICE,
    torch_dtype=TORCH_DTYPE,
    truncation=True,
    max_length=256
)
hin_analyzer = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-xlm-roberta-base-sentiment",
    device=DEVICE,
    torch_dtype=TORCH_DTYPE,
    truncation=True,
    max_length=256

)

emotion_analyzer = pipeline(
    "text-classification",
    model="SamLowe/roberta-base-go_emotions",
    device=DEVICE,
    torch_dtype=TORCH_DTYPE,
    truncation=True,
    max_length=256
)

def _is_hinglish(text: str) -> bool:
    """Detects whether the message contains Hindi script or common Hinglish markers."""
    text_lower = text.lower()
    hinglish_markers = {
        "bhai", "kya", "hai", "nahi", "toh", "aur", "ye", "wo", "kaise", 
        "hoga", "karo", "accha", "yaar", "paisa", "loot", "sahi", "sab"
    }
    # Check marker words
    if any(marker in text_lower.split() for marker in hinglish_markers):
        return True
    try:
        lang = detect(text)
        return lang in ["hi", "mr", "ne"]
    except Exception:
        return False

def analyze_and_store_sentiment(batch_size: int = 200) -> int:
    """
    Fetches unanalyzed messages from PostgreSQL, executes GPU batched inference,
    and updates the sentiment_results table.
    """
    fetch_query = """
        SELECT m.message_id, m.text, m.timestamp
        FROM messages m
        LEFT JOIN sentiment_results s ON m.message_id = s.message_id
        WHERE s.message_id IS NULL AND m.text IS NOT NULL AND trim(m.text) != ''
        ORDER BY m.timestamp ASC
        LIMIT %s;
    """

    insert_query = """
        INSERT INTO sentiment_results (message_id, label, confidence, score, timestamp)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (message_id) DO NOTHING;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(fetch_query, (batch_size,))
            rows = cur.fetchall()

            if not rows:
                logger.info("No unanalyzed messages to process.")
                return 0

            msg_ids = [r[0] for r in rows]
            texts = [r[1][:256] for r in rows]
            timestamps = [r[2] for r in rows]

            # Split texts into language buckets for dedicated routing
            hinglish_indices = []
            english_indices = []
            for i, text in enumerate(texts):
                if _is_hinglish(text):
                    hinglish_indices.append(i)
                else:
                    english_indices.append(i)

            sentiment_outputs = [None] * len(texts)

            # Batched GPU Sentiment Inference
            if english_indices:
                eng_texts = [texts[i] for i in english_indices]
                eng_preds = eng_analyzer(eng_texts, batch_size=32)
                for idx, pred in zip(english_indices, eng_preds):
                    sentiment_outputs[idx] = pred

            if hinglish_indices:
                hin_texts = [texts[i] for i in hinglish_indices]
                hin_preds = hin_analyzer(hin_texts, batch_size=32)
                for idx, pred in zip(hinglish_indices, hin_preds):
                    sentiment_outputs[idx] = pred

            # Batched GPU Granular Emotion Inference across all texts
            emotion_preds = emotion_analyzer(texts, batch_size=32)

            records = []
            for i in range(len(rows)):
                sent_label = sentiment_outputs[i]["label"].lower()
                sent_score = float(sentiment_outputs[i]["score"])
                emotion_label = emotion_preds[i]["label"].lower()

                # Normalize polarity score to a -1.0 to 1.0 continuous scale for timeline charting
                if "neg" in sent_label:
                    compound_score = -sent_score
                    clean_label = "negative"
                elif "pos" in sent_label:
                    compound_score = sent_score
                    clean_label = "positive"
                else:
                    compound_score = 0.0
                    clean_label = "neutral"

                # Composite tag (e.g., "negative:annoyance" or "positive:joy")
                composite_label = f"{clean_label}:{emotion_label}"

                records.append((
                    msg_ids[i],
                    composite_label,
                    sent_score,
                    compound_score,
                    timestamps[i]
                ))

            cur.executemany(insert_query, records)
            conn.commit()
            logger.info(f"Successfully processed and stored GPU sentiment scores for {len(records)} messages.")
            return len(records)


def export_sentiment_to_csv(output_path: str = "data/sentiment_results.csv") -> str:
    """Exports processed sentiment analysis and message logs into a structured CSV file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    query = """
        SELECT 
            m.message_id,
            m.channel_id,
            m.user_id,
            m.timestamp,
            m.text,
            COALESCE(s.label, 'unprocessed') AS sentiment_emotion,
            COALESCE(s.confidence, 0.0) AS confidence,
            COALESCE(s.score, 0.0) AS polarity_score
        FROM messages m
        LEFT JOIN sentiment_results s ON m.message_id = s.message_id
        ORDER BY m.timestamp DESC;
    """

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]

    with open(output_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(rows)

    logger.info(f"Exported {len(rows)} records to {output_path}")
    return output_path

if __name__ == "__main__":
    print("Running GPU sentiment scoring...")
    scored = analyze_and_store_sentiment(batch_size=200)
    print(f"Scored {scored} messages.")
    
    csv_file = export_sentiment_to_csv("data/sentiment_results.csv")
    print(f"Exported data to {csv_file}")