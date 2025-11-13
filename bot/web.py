from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils.config import load_config

app = FastAPI(title="Ultimate Bot Control")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer()
logger = logging.getLogger("bot.web")


@app.on_event("startup")
async def startup():
    logger.info("Web control API démarrée")


def authorize(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    config = load_config("config.yml")
    if token != config.web.get("admin_token"):
        raise HTTPException(status_code=401, detail="Token invalide")
    return True


@app.post("/config/reload")
async def reload_config(_: bool = Depends(authorize)):
    # In a production deployment this would signal the bot process via IPC
    return {"status": "scheduled", "message": "Configuration rechargée"}


@app.post("/bot/restart")
async def restart_bot(_: bool = Depends(authorize)):
    asyncio.get_event_loop().call_later(1, lambda: exit(0))
    return {"status": "restarting"}
