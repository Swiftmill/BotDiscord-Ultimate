from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class LicenseCreate(BaseModel):
    owner: str
    key: str = Field(..., min_length=16)
    expires_at: Optional[datetime]
    max_guilds: int = 1
    notes: str = ""


class LicenseUpdate(BaseModel):
    owner: Optional[str]
    expires_at: Optional[datetime]
    max_guilds: Optional[int]
    is_active: Optional[bool]
    banned: Optional[bool]
    guild_id: Optional[str]
    notes: Optional[str]


class LicenseResponse(BaseModel):
    key: str
    owner: str
    expires_at: Optional[datetime]
    max_guilds: int
    guild_id: Optional[str]
    is_active: bool
    banned: bool
    notes: str

    class Config:
        orm_mode = True


class LicenseValidationRequest(BaseModel):
    key: str
    guild_id: str
    machine_fingerprint: str


class LicenseValidationResponse(BaseModel):
    valid: bool
    reason: str
    expires_at: Optional[datetime]


class AuditLogResponse(BaseModel):
    action: str
    actor: str
    message: str
    created_at: datetime

    class Config:
        orm_mode = True
