import os
import json
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv

from app.models import User, Message

load_dotenv()

DB_NAME = os.getenv("POSTGRES_DB", "social_analytics")
DB_USER = os.getenv("POSTGRES_USER", "sihadmin")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "1234")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DSN = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

@contextmanager
def get_db_connection():
    """Provides a transactional database connection scope."""
    conn = psycopg2.connect(DSN)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_postgres_db():
    """Initializes standard tables, constraints, and indexes."""
    ddl = """
    CREATE TABLE IF NOT EXISTS users (
        user_id VARCHAR(128) PRIMARY KEY,
        platform VARCHAR(32) NOT NULL,
        username VARCHAR(255),
        display_name VARCHAR(255),
        bio TEXT,
        language_code VARCHAR(16),
        is_bot BOOLEAN DEFAULT FALSE,
        verified BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP WITHOUT TIME ZONE,
        first_seen_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS messages (
        message_id VARCHAR(128) NOT NULL,
        platform VARCHAR(32) NOT NULL,
        channel_id VARCHAR(128) NOT NULL,
        user_id VARCHAR(128),
        text TEXT,
        timestamp TIMESTAMP WITHOUT TIME ZONE NOT NULL,
        views INTEGER DEFAULT 0,
        forwards INTEGER DEFAULT 0,
        replies_count INTEGER DEFAULT 0,
        reply_to_msg_id VARCHAR(128),
        forward_from_id VARCHAR(128),
        hashtags JSONB DEFAULT '[]'::jsonb,
        mentions JSONB DEFAULT '[]'::jsonb,
        raw_metadata JSONB DEFAULT '{}'::jsonb,
        PRIMARY KEY (platform, channel_id, message_id)
    );

    CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp DESC);
    CREATE INDEX IF NOT EXISTS idx_messages_channel ON messages(channel_id);
    CREATE INDEX IF NOT EXISTS idx_messages_user ON messages(user_id);
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(ddl)

def upsert_user(user: User):
    """Inserts or updates a user profile."""
    query = """
    INSERT INTO users (
        user_id, platform, username, display_name, bio,
        language_code, is_bot, verified, created_at, first_seen_at
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (user_id) DO UPDATE SET
        username = EXCLUDED.username,
        display_name = EXCLUDED.display_name,
        bio = EXCLUDED.bio,
        language_code = EXCLUDED.language_code,
        verified = EXCLUDED.verified;
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (
                user.user_id, user.platform, user.username, user.display_name,
                user.bio, user.language_code, user.is_bot, user.verified,
                user.created_at, user.first_seen_at
            ))

def save_messages(messages: list[Message]):
    """Batch-inserts or updates messages."""
    if not messages:
        return

    query = """
    INSERT INTO messages (
        message_id, platform, channel_id, user_id, text,
        timestamp, views, forwards, replies_count,
        reply_to_msg_id, forward_from_id, hashtags, mentions, raw_metadata
    ) VALUES %s
    ON CONFLICT (platform, channel_id, message_id) DO UPDATE SET
        views = EXCLUDED.views,
        forwards = EXCLUDED.forwards,
        replies_count = EXCLUDED.replies_count;
    """
    records = [
        (
            m.message_id, m.platform, m.channel_id, m.user_id, m.text,
            m.timestamp, m.views, m.forwards, m.replies_count,
            m.reply_to_msg_id, m.forward_from_id,
            json.dumps(m.hashtags), json.dumps(m.mentions), json.dumps(m.raw_metadata)
        )
        for m in messages
    ]

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            execute_values(cur, query, records)