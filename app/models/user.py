from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: str = Field(..., description="Unique platform-scoped or global user identifier")
    platform: str = Field(default="telegram", description="Origin platform name")
    username: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    language_code: Optional[str] = None
    is_bot: bool = False
    verified: bool = False
    created_at: Optional[datetime] = None
    first_seen_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        from_attributes = True