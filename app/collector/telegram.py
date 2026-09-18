import os
import re
import logging
import asyncio
from datetime import datetime
from typing import List, Tuple, Optional

from telethon import TelegramClient, events
from telethon.tl.functions.users import GetFullUserRequest
from telethon.errors import FloodWaitError
from telethon.tl.types import (
    User as TelethonUser,
    Channel as TelethonChannel,
    MessageMediaPhoto,
    MessageMediaDocument
)
from dotenv import load_dotenv

from app.models import User, Message, Interaction, InteractionType
from app.database.postgres import save_messages, upsert_user
from app.database.neo4j import neo4j_client

load_dotenv()
logger = logging.getLogger("telegram_collector")
logging.basicConfig(level=logging.INFO)

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_NAME = os.getenv("TELEGRAM_SESSION_NAME", "analytics_session")

class TelegramCollector:
    def __init__(self):
        self.client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
        self.processed_users = set()

    async def start(self):
        """Authenticates and boots the Telethon MTProto client session."""
        await self.client.start(phone=lambda: os.getenv("TELEGRAM_PHONE"))
        logger.info("Telegram client successfully authenticated.")

    async def stop(self):
        """Disconnects the client cleanly."""
        await self.client.disconnect()
        logger.info("Telegram client disconnected.")

    @staticmethod
    def _extract_entities(text: str) -> Tuple[List[str], List[str]]:
        """Extracts hashtags and mentions via regex."""
        if not text:
            return [], []
        hashtags = [tag.strip("#") for tag in re.findall(r"#\w+", text)]
        mentions = [mention.strip("@") for mention in re.findall(r"@\w+", text)]
        return hashtags, mentions

    async def _normalize_user(self, sender) -> Optional[User]:
        if not sender:
            return None

        if isinstance(sender, TelethonUser):
            first = sender.first_name or ""
            last = sender.last_name or ""
            full_name = f"{first} {last}".strip() or None
            
            bio_text = None
            if sender.id not in self.processed_users and not sender.bot:
                try:
                    full_user = await self.client(GetFullUserRequest(sender))
                    bio_text = full_user.full_user.about
                    self.processed_users.add(sender.id)
                    await asyncio.sleep(0.5) 
                except FloodWaitError as e:
                    logger.warning(f"Rate limited. Skipping bios for {e.seconds}s.")
                except Exception:
                    pass 

            return User(
                user_id=f"tg_{sender.id}",
                platform="telegram",
                username=sender.username,
                display_name=full_name,
                bio=bio_text,
                language_code=sender.lang_code,
                is_bot=sender.bot or False,
                verified=sender.verified or False
            )
        return None

    def _normalize_message(self, msg, channel_id: str) -> Tuple[Message, List[Interaction]]:
        """Transforms raw Telethon message into common Message & Interaction records."""
        text = msg.message or ""
        hashtags, mentions = self._extract_entities(text)
        interactions: List[Interaction] = []

        sender_id = f"tg_{msg.sender_id}" if msg.sender_id else None

        # 1. Forward Interactions
        forward_from_id = None
        if msg.forward:
            if msg.forward.sender_id:
                forward_from_id = f"tg_{msg.forward.sender_id}"
            elif msg.forward.chat_id:
                forward_from_id = f"tg_chan_{msg.forward.chat_id}"

            if sender_id and forward_from_id:
                interactions.append(Interaction(
                    source_id=sender_id,
                    target_id=forward_from_id,
                    interaction_type=InteractionType.FORWARD,
                    channel_id=channel_id,
                    timestamp=msg.date
                ))

        # 2. Reply Interactions
        reply_to_msg_id = None
        if msg.reply_to:
            reply_to_msg_id = str(msg.reply_to.reply_to_msg_id)
            if sender_id:
                interactions.append(Interaction(
                    source_id=sender_id,
                    target_id=f"tg_msg_{channel_id}_{reply_to_msg_id}",
                    interaction_type=InteractionType.REPLY,
                    channel_id=channel_id,
                    timestamp=msg.date
                ))

        # 3. Mention Interactions
        if sender_id:
            for mention in mentions:
                interactions.append(Interaction(
                    source_id=sender_id,
                    target_id=f"tg_user_{mention}",
                    interaction_type=InteractionType.MENTION,
                    channel_id=channel_id,
                    timestamp=msg.date
                ))

        has_media = bool(isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument)))

        normalized_msg = Message(
            message_id=str(msg.id),
            platform="telegram",
            channel_id=channel_id,
            user_id=sender_id,
            text=text,
            timestamp=msg.date,
            views=msg.views or 0,
            forwards=msg.forwards or 0,
            replies_count=msg.replies.replies if msg.replies else 0,
            reply_to_msg_id=reply_to_msg_id,
            forward_from_id=forward_from_id,
            hashtags=hashtags,
            mentions=mentions,
            raw_metadata={"has_media": has_media, "edit_date": str(msg.edit_date) if msg.edit_date else None}
        )

        return normalized_msg, interactions

    async def fetch_history_multiple(self, channels: List[str], limit: int = 300):
        for channel_identifier in channels:
            logger.info(f"--- Starting ingestion for {channel_identifier} ---")
            try:
                entity = await self.client.get_entity(channel_identifier)
                channel_id = str(entity.id)
                neo4j_client.upsert_channel_node(channel_id=channel_id, platform="telegram")

                messages_batch = []
                async for raw_msg in self.client.iter_messages(entity, limit=limit):
                    sender = await raw_msg.get_sender()
                    norm_user = await self._normalize_user(sender)
                    
                    if norm_user:
                        upsert_user(norm_user)
                        neo4j_client.upsert_user_node(norm_user.user_id, norm_user.platform, norm_user.username)

                    norm_msg, interactions = self._normalize_message(raw_msg, channel_id)
                    messages_batch.append(norm_msg)

                    for interaction in interactions:
                        neo4j_client.add_interaction(interaction)

                save_messages(messages_batch)
                logger.info(f"Stored {len(messages_batch)} messages from {channel_identifier}.")
            
            except Exception as e:
                logger.error(f"Failed to fetch {channel_identifier}: {e}")

    async def listen_live(self, target_channels: list):
        """Continuously streams incoming messages and interaction edges."""
        logger.info(f"Starting real-time streaming listener on {target_channels}...")

        @self.client.on(events.NewMessage(chats=target_channels))
        async def handler(event):
            raw_msg = event.message
            channel_id = str(event.chat_id)

            sender = await event.get_sender()
            norm_user = self._normalize_user(sender)
            if norm_user:
                upsert_user(norm_user)
                neo4j_client.upsert_user_node(norm_user.user_id, norm_user.platform, norm_user.username)

            norm_msg, interactions = self._normalize_message(raw_msg, channel_id)
            save_messages([norm_msg])

            for interaction in interactions:
                neo4j_client.add_interaction(interaction)

            logger.info(f"Real-time event processed: Message {norm_msg.message_id} from {channel_id}")

        await self.client.run_until_disconnected()