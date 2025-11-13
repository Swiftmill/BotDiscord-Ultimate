from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .database import AuditLog, License, get_license, get_session
from .models import (
    AuditLogResponse,
    LicenseCreate,
    LicenseResponse,
    LicenseUpdate,
    LicenseValidationRequest,
    LicenseValidationResponse,
)
from .security import create_access_token, decode_access_token
from .settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.app_name)
security = HTTPBearer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def rate_limit(request: Request) -> None:
    bucket = request.client.host
    store = request.app.state.__dict__.setdefault("rate_limit", {})
    history = store.setdefault(bucket, [])
    now = datetime.utcnow()
    history[:] = [ts for ts in history if (now - ts).seconds < 60]
    if len(history) >= settings.rate_limit_per_minute:
        await asyncio.sleep(1)
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Rate limit exceeded")
    history.append(now)


async def authorize(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = credentials.credentials
    payload = decode_access_token(token)
    return payload["sub"]


@app.post("/auth/token")
async def issue_token(password: str):
    if password != settings.secret_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    token, expires = create_access_token("admin")
    return {"token": token, "expires": expires}


@app.post("/licenses", response_model=LicenseResponse, dependencies=[Depends(rate_limit)])
async def create_license(data: LicenseCreate, _: str = Depends(authorize)):
    with get_session() as session:
        if get_license(session, data.key):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="License key already exists")
        license_obj = License(
            key=data.key,
            owner=data.owner,
            expires_at=data.expires_at,
            max_guilds=data.max_guilds,
            notes=data.notes,
        )
        session.add(license_obj)
        session.add(
            AuditLog(
                license_key=data.key,
                action="create",
                actor="admin",
                message=f"License created for {data.owner}",
            )
        )
        session.commit()
        session.refresh(license_obj)
        return license_obj


@app.get("/licenses", response_model=List[LicenseResponse])
async def list_licenses(_: str = Depends(authorize)):
    with get_session() as session:
        return session.query(License).all()


@app.get("/licenses/{license_key}", response_model=LicenseResponse)
async def get_license_route(license_key: str, _: str = Depends(authorize)):
    with get_session() as session:
        license_obj = get_license(session, license_key)
        if not license_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License not found")
        return license_obj


@app.put("/licenses/{license_key}", response_model=LicenseResponse)
async def update_license(license_key: str, data: LicenseUpdate, _: str = Depends(authorize)):
    with get_session() as session:
        license_obj = get_license(session, license_key)
        if not license_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License not found")
        for field, value in data.dict(exclude_unset=True).items():
            setattr(license_obj, field, value)
        session.add(
            AuditLog(
                license_key=license_key,
                action="update",
                actor="admin",
                message=f"Fields updated: {', '.join(data.dict(exclude_unset=True).keys())}",
            )
        )
        session.commit()
        session.refresh(license_obj)
        return license_obj


@app.delete("/licenses/{license_key}")
async def delete_license(license_key: str, _: str = Depends(authorize)):
    with get_session() as session:
        license_obj = get_license(session, license_key)
        if not license_obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="License not found")
        session.delete(license_obj)
        session.add(
            AuditLog(
                license_key=license_key,
                action="delete",
                actor="admin",
                message="License deleted",
            )
        )
        session.commit()
        return {"status": "deleted"}


@app.post("/licenses/validate", response_model=LicenseValidationResponse, dependencies=[Depends(rate_limit)])
async def validate_license(data: LicenseValidationRequest):
    with get_session() as session:
        license_obj = get_license(session, data.key)
        if not license_obj:
            return LicenseValidationResponse(valid=False, reason="License not found", expires_at=None)
        if not license_obj.is_active or license_obj.banned:
            return LicenseValidationResponse(valid=False, reason="License inactive", expires_at=license_obj.expires_at)
        if license_obj.expires_at and license_obj.expires_at < datetime.utcnow():
            license_obj.is_active = False
            session.commit()
            return LicenseValidationResponse(valid=False, reason="License expired", expires_at=license_obj.expires_at)
        if license_obj.guild_id and license_obj.guild_id != data.guild_id:
            return LicenseValidationResponse(valid=False, reason="License bound to another guild", expires_at=license_obj.expires_at)
        if not license_obj.guild_id:
            license_obj.guild_id = data.guild_id
        license_obj.updated_at = datetime.utcnow()
        session.add(
            AuditLog(
                license_key=data.key,
                action="validate",
                actor="bot",
                message=f"Validation succeeded for guild {data.guild_id}",
            )
        )
        session.commit()
        return LicenseValidationResponse(valid=True, reason="Valid", expires_at=license_obj.expires_at)


@app.get("/licenses/{license_key}/logs", response_model=List[AuditLogResponse])
async def license_logs(license_key: str, _: str = Depends(authorize)):
    with get_session() as session:
        logs = session.query(AuditLog).filter(AuditLog.license_key == license_key).order_by(AuditLog.created_at.desc()).all()
        return logs


@app.on_event("startup")
async def ensure_antivirus_file():
    path = Path(settings.antivirus_hash_db)
    path.touch(exist_ok=True)


if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=False)
