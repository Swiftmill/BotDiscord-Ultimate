from __future__ import annotations

import asyncio
import logging
from pathlib import Path

import discord
from discord.ext import commands

from utils.config import Config, load_config
from utils.logger import setup_logger
from utils.license import ensure_license

CONFIG_PATH = Path("config.yml")


class UltimateBot(commands.Bot):
    def __init__(self, config: Config):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = config.bot.get("intents", {}).get("message_content", False)
        super().__init__(command_prefix=config.bot.get("command_prefix", "!"), intents=intents)
        self.config = config
        self.logger = setup_logger(config.logging.get("level", "INFO"), config.logging.get("file", "logs/bot.log"))

    async def setup_hook(self) -> None:
        await ensure_license(self.config.license, [str(gid) for gid in self.config.bot.get("guild_ids", [])])
        await self.load_extension("cogs.security")
        await self.load_extension("cogs.automod")
        await self.load_extension("cogs.tickets")
        await self.load_extension("cogs.music")
        self.tree.copy_global_to(guild=None)

    async def on_ready(self):
        activity_type = self.config.bot.get("activity_type", "playing").lower()
        activity_map = {
            "playing": discord.ActivityType.playing,
            "watching": discord.ActivityType.watching,
            "listening": discord.ActivityType.listening,
        }
        activity = discord.Activity(type=activity_map.get(activity_type, discord.ActivityType.playing), name=self.config.bot.get("status", "Online"))
        await self.change_presence(status=discord.Status.online, activity=activity)
        self.logger.info("Bot connecté en tant que %s", self.user)


async def run_bot():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Config file missing. Copy bot/config_example.yml to bot/config.yml")
    config = load_config(CONFIG_PATH)
    bot = UltimateBot(config)
    async with bot:
        await bot.start(config.bot["token"])


if __name__ == "__main__":
    asyncio.run(run_bot())
