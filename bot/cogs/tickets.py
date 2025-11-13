from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path

import discord
from discord import app_commands
from discord.ext import commands

log = logging.getLogger("bot.tickets")


class TicketManager:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def create_transcription(self, channel: discord.TextChannel, messages: list[discord.Message]):
        file_path = self.base_path / f"ticket-{channel.id}-{datetime.utcnow().isoformat()}.md"
        with file_path.open("w", encoding="utf-8") as fp:
            fp.write(f"# Transcription pour {channel.name}\n\n")
            for message in messages:
                timestamp = message.created_at.isoformat()
                fp.write(f"[{timestamp}] {message.author}: {message.clean_content}\n")
        return file_path


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = TicketManager(Path("tickets"))

    @app_commands.command(name="ticket", description="Créer un ticket support")
    async def ticket(self, interaction: discord.Interaction, category: str = "Support"):
        guild = interaction.guild
        category_channel = discord.utils.get(guild.categories, name=category)
        if not category_channel:
            category_channel = await guild.create_category(category)
        ticket_channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category_channel,
            topic=f"Ticket ouvert par {interaction.user}",
            reason="Ticket support",
            overwrites={
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            },
        )
        await ticket_channel.send(f"🎫 Ticket créé par {interaction.user.mention}. Un membre du staff vous répondra bientôt.")
        await interaction.response.send_message(f"Votre ticket a été créé: {ticket_channel.mention}", ephemeral=True)

    @app_commands.command(name="ticket-close", description="Fermer un ticket")
    async def ticket_close(self, interaction: discord.Interaction):
        channel = interaction.channel
        if not isinstance(channel, discord.TextChannel) or not channel.name.startswith("ticket"):
            await interaction.response.send_message("Commande uniquement disponible dans un ticket.", ephemeral=True)
            return
        messages = [message async for message in channel.history(limit=200)]
        transcription = self.manager.create_transcription(channel, list(reversed(messages)))
        log_channel_id = self.bot.config.security.get("ticket_log_channel_id")
        if log_channel_id:
            log_channel = interaction.guild.get_channel(int(log_channel_id))
            if log_channel:
                await log_channel.send(file=discord.File(transcription))
        await channel.send("Ticket fermé. Transcription archivée.")
        await asyncio.sleep(5)
        await channel.delete(reason="Ticket fermé")
        await interaction.response.send_message("Ticket fermé avec succès.", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(TicketCog(bot))
