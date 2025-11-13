from __future__ import annotations

import asyncio
import hashlib
from collections import defaultdict, deque
from datetime import datetime, timedelta
from pathlib import Path
from typing import Deque, Dict

import aiohttp


class SecurityManager:
    def __init__(self, config: dict):
        self.config = config
        self.joins: Deque[datetime] = deque()
        self.message_history: Dict[int, Deque[datetime]] = defaultdict(deque)
        self.duplicate_tracker: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
        self.emoji_tracker: Dict[int, Deque[datetime]] = defaultdict(deque)
        self.user_scores: Dict[int, int] = defaultdict(int)
        self.antivirus_hashes = self._load_antivirus_hashes()

    def _load_antivirus_hashes(self) -> set[str]:
        path = Path(self.config.get("antivirus_hash_db", ""))
        if path.exists():
            return {line.strip() for line in path.read_text().splitlines() if line and not line.startswith("#")}
        return set()

    def record_join(self) -> None:
        now = datetime.utcnow()
        self.joins.append(now)
        window = timedelta(seconds=self.config.get("raid_window_seconds", 30))
        while self.joins and now - self.joins[0] > window:
            self.joins.popleft()

    def is_raid(self) -> bool:
        return len(self.joins) >= self.config.get("raid_threshold", 5)

    def record_message(self, user_id: int, content: str) -> Dict[str, bool]:
        now = datetime.utcnow()
        window = timedelta(seconds=self.config.get("spam_window_seconds", 8))
        history = self.message_history[user_id]
        history.append(now)
        while history and now - history[0] > window:
            history.popleft()
        spam = len(history) >= self.config.get("spam_threshold", 5)

        duplicates = self.duplicate_tracker[user_id]
        duplicates[content] += 1
        flood = duplicates[content] >= self.config.get("flood_duplicate_threshold", 4)
        for key in list(duplicates.keys()):
            if duplicates[key] == 0:
                del duplicates[key]

        emoji_window = self.emoji_tracker[user_id]
        emoji_window.append(now)
        while emoji_window and now - emoji_window[0] > window:
            emoji_window.popleft()

        return {"spam": spam, "flood": flood}

    def suspicious_score(self, user_id: int, amount: int) -> int:
        self.user_scores[user_id] += amount
        return self.user_scores[user_id]

    async def is_malicious_attachment(self, file_bytes: bytes) -> bool:
        digest = hashlib.sha256(file_bytes).hexdigest()
        if digest in self.antivirus_hashes:
            return True
        # Simulated asynchronous scan placeholder - extend with real API
        await asyncio.sleep(0)
        return False

    @staticmethod
    def caps_ratio(content: str) -> float:
        letters = [c for c in content if c.isalpha()]
        if not letters:
            return 0.0
        upper = sum(1 for c in letters if c.isupper())
        return upper / len(letters)

    @staticmethod
    def emoji_count(content: str) -> int:
        return sum(1 for c in content if ord(c) > 10000)


async def fetch_lyrics(query: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get("https://api.lyrics.ovh/v1/", params={"q": query}) as resp:
            if resp.status != 200:
                return "Lyrics not found."
            data = await resp.json()
            return data.get("lyrics", "Lyrics unavailable.")
