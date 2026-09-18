from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class Message(BaseModel):
    message_id: str = Field(..., description="Unique ID within the platform/channel")
    platform: str = Field(default="telegram", description="Origin platform")
    channel_id: str = Field(..., description="Channel, chat, or group identifier")
    user_id: Optional[str] = Field(None, description="Author user ID if available")
    text: str = Field(default="", description="Cleaned or raw post text content")
    timestamp: datetime = Field(..., description="Publication UTC timestamp")
    views: int = Field(default=0, ge=0)
    forwards: int = Field(default=0, ge=0)
    replies_count: int = Field(default=0, ge=0)
    reply_to_msg_id: Optional[str] = None
    forward_from_id: Optional[str] = None
    hashtags: List[str] = Field(default_factory=list)
    mentions: List[str] = Field(default_factory=list)
    raw_metadata: dict = Field(default_factory=dict, description="Raw source metadata backup")

    class Config:
        from_attributes = True