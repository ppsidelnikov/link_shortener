"""
Схемы Pydantic для ссылок
"""

from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional

class LinkBase(BaseModel):
    original_url: HttpUrl 

class LinkCreate(LinkBase):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(
        None, 
        min_length=4, 
        max_length=16,
        pattern="^[a-zA-Z0-9_-]+$"  
    )
    expires_in_minutes: Optional[int] = Field(
        None,
        description="Link lifetime in minutes"
    )

    @validator('expires_in_minutes')
    def validate_expires_in_minutes(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Expiration time must be positive")
        return v

class LinkResponse(LinkBase):
    original_url: HttpUrl
    short_code: str
    created_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    owner_id: Optional[int] = None

    class Config:
        from_attributes = True  


class LinkUpdate(BaseModel):
    new_url: HttpUrl 

class LinkStats(BaseModel):
    short_code: str
    original_url: str
    access_count: int
    expires_at: datetime | None
    last_accessed: datetime | None

    class Config:
        from_attributes = True