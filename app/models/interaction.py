from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class InteractionType(str, Enum):
    REPLY = "REPLIED_TO"
    FORWARD = "FORWARDED_FROM"
    MENTION = "MENTIONED"
    REACTION = "REACTED"

class Interaction(BaseModel):
    source_id: str = Field(..., description="Source node ID (actor)")
    target_id: str = Field(..., description="Target node ID (receiver/referenced)")
    interaction_type: InteractionType
    channel_id: str = Field(..., description="Context channel or chat ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    weight: float = Field(default=1.0, description="Strength or count of interaction")
    metadata: dict = Field(default_factory=dict)

    class Config:
        from_attributes = True