from __future__ import annotations

from pathlib import Path

import discord
from discord.ext import commands


class AutoModCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bad_words = self._load_words("bot/assets/bad_words.txt")
        self.whitelisted_links = self._load_words("bot/assets/allowed_links.txt")

    def _load_words(self, path: str) -> set[str]:
        file = Path(path)
        if not file.exists():
            return set()
        return {line.strip().lower() for line in file.read_text(encoding="utf-8").splitlines() if line}

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        lowered = message.content.lower()
        if any(word in lowered for word in self.bad_words):
            await message.delete()
            await message.channel.send(f"🚫 {message.author.mention}, langage inapproprié interdit.", delete_after=5)
        if lowered.isupper() and len(lowered) > 5:
            await message.delete()
            await message.channel.send("Merci d'éviter les majuscules.", delete_after=5)
        if lowered.count("!") > 5:
            await message.delete()
        if any(emoji in message.content for emoji in ["😂", "🤣", "😍"]) and message.content.count(emoji := "😂") > 5:
            await message.delete()
        if "http" in lowered:
            if not any(allowed in lowered for allowed in self.whitelisted_links):
                await message.delete()
                await message.channel.send("Lien non autorisé supprimé.", delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(AutoModCog(bot))
