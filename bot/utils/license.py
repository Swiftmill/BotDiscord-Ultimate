from __future__ import annotations

import asyncio
import hashlib
from typing import Any, Dict

import aiohttp


class LicenseValidationError(Exception):
    """Raised when license validation fails."""


async def validate_license(config: Dict[str, Any], guild_id: str) -> Dict[str, Any]:
    payload = {
        "key": config["key"],
        "guild_id": guild_id,
        "machine_fingerprint": hashlib.sha256(guild_id.encode()).hexdigest(),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(config["endpoint"], json=payload) as resp:
            data = await resp.json()
            if not data.get("valid"):
                raise LicenseValidationError(data.get("reason", "Unknown error"))
            return data


async def ensure_license(config: Dict[str, Any], guild_ids: list[str]) -> None:
    await asyncio.gather(*(validate_license(config, gid) for gid in guild_ids or ["standalone"]))
