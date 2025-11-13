from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands, tasks

from ..utils.security import SecurityManager

log = logging.getLogger("bot.security")


class SecurityCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict):
        self.bot = bot
        self.config = config
        self.manager = SecurityManager(config)
        self.raid_monitor.start()

    def cog_unload(self) -> None:
        self.raid_monitor.cancel()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.manager.record_join()
        if self.manager.is_raid():
            log.warning("Raid detected - enabling lockdown mode")
            await self._lockdown(member.guild)

    async def _lockdown(self, guild: discord.Guild):
        for channel in guild.text_channels:
            try:
                overwrite = channel.overwrites_for(guild.default_role)
                overwrite.send_messages = False
                await channel.set_permissions(guild.default_role, overwrite=overwrite, reason="Raid lockdown")
            except discord.Forbidden:
                log.error("Missing permissions to lockdown %s", channel.name)
        await guild.system_channel.send("⚠️ Raid détecté, serveur verrouillé temporairement !") if guild.system_channel else None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        flags = self.manager.record_message(message.author.id, message.content)
        caps_ratio = SecurityManager.caps_ratio(message.content)
        emoji_count = SecurityManager.emoji_count(message.content)
        suspicious_score = 0

        if flags["spam"]:
            suspicious_score += 3
        if flags["flood"]:
            suspicious_score += 2
        if caps_ratio > self.config.get("max_caps_percentage", 0.7):
            suspicious_score += 2
        if emoji_count > self.config.get("emoji_spam_threshold", 8):
            suspicious_score += 2
        if "http" in message.content:
            suspicious_score += 1
        if any(phrase in message.content.lower() for phrase in ["token", "nitro", "free", "http"]):
            suspicious_score += 1

        score = self.manager.suspicious_score(message.author.id, suspicious_score)
        if score >= self.config.get("suspicious_score_threshold", 10):
            await self.apply_sanction(message, score)

        await self.detect_links(message)

    async def detect_links(self, message: discord.Message):
        if "http" not in message.content:
            return
        disallowed = ["grab", "steal", "phish"]
        if any(keyword in message.content.lower() for keyword in disallowed):
            await message.delete()
            await self.warn_user(message.author, "Lien suspect détecté")

    async def warn_user(self, member: discord.Member, reason: str):
        try:
            await member.send(f"⚠️ Avertissement: {reason}")
        except discord.Forbidden:
            pass

    async def apply_sanction(self, message: discord.Message, score: int):
        guild = message.guild
        if score < 12:
            await self.warn_user(message.author, "Comportement suspect")
        elif score < 15:
            mute_role = discord.utils.get(guild.roles, name="Muted")
            if mute_role:
                await message.author.add_roles(mute_role, reason="Automod mute")
        elif score < 18:
            await guild.kick(message.author, reason="Kick automatique: comportement suspect")
        else:
            await guild.ban(message.author, reason="Ban automatique: comportement dangereux")
        try:
            await message.delete()
        except discord.Forbidden:
            log.error("Impossible de supprimer un message suspect")

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.attachments:
            await self.scan_attachments(message)

    async def scan_attachments(self, message: discord.Message):
        for attachment in message.attachments:
            file_bytes = await attachment.read(use_cached=True)
            malicious = await self.manager.is_malicious_attachment(file_bytes)
            if malicious:
                await message.author.ban(reason="Malware détecté")
                await message.channel.send(f"🚨 Malware détecté dans {attachment.filename}, utilisateur banni.")

    @tasks.loop(seconds=60)
    async def raid_monitor(self):
        if self.manager.is_raid():
            log.info("Raid monitor triggered - lockdown in effect")

    @raid_monitor.before_loop
    async def before_raid_monitor(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    config = bot.config.security
    await bot.add_cog(SecurityCog(bot, config))
