from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands
from yt_dlp import YoutubeDL

from ..utils.security import fetch_lyrics


YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "default_search": "auto",
    "noplaylist": True,
}
FFMPEG_OPTIONS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn",
}


def create_source(url: str):
    with YoutubeDL(YDL_OPTIONS) as ydl:
        info = ydl.extract_info(url, download=False)
        if "entries" in info:
            info = info["entries"][0]
        return info["url"], info["title"], info.get("duration")


@dataclass
class MusicTrack:
    url: str
    title: str
    duration: Optional[int]
    requester: discord.Member
class MusicCog(commands.Cog):
    def __init__(self, bot: commands.Bot, config: dict):
        self.bot = bot
        self.config = config
        self.queue = asyncio.Queue()
        self.current: Optional[MusicTrack] = None
        self.player_task = self.bot.loop.create_task(self.player_loop())

    def cog_unload(self) -> None:
        self.player_task.cancel()

    async def player_loop(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            self.current = await self.queue.get()
            if not self.current:
                continue
            voice_client = self.current.requester.guild.voice_client
            if not voice_client:
                continue
            source_url, _, _ = create_source(self.current.url)
            audio = discord.FFmpegPCMAudio(source_url, **FFMPEG_OPTIONS)
            voice_client.play(audio)
            while voice_client.is_playing():
                await asyncio.sleep(1)

    async def ensure_voice(self, interaction: discord.Interaction):
        if not interaction.user.voice:
            await interaction.response.send_message("Rejoins un salon vocal pour utiliser la musique.", ephemeral=True)
            return False
        voice_channel = interaction.user.voice.channel
        if not interaction.guild.voice_client:
            await voice_channel.connect()
        elif interaction.guild.voice_client.channel != voice_channel:
            await interaction.guild.voice_client.move_to(voice_channel)
        return True

    @app_commands.command(name="play", description="Lire un titre")
    async def play(self, interaction: discord.Interaction, query: str):
        if not await self.ensure_voice(interaction):
            return
        url, title, duration = create_source(query)
        track = MusicTrack(url=url, title=title, duration=duration, requester=interaction.user)
        await self.queue.put(track)
        await interaction.response.send_message(f"🎶 Ajouté à la file: **{title}**")

    @app_commands.command(name="pause", description="Mettre en pause")
    async def pause(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            await interaction.response.send_message("⏸️ Pause activée")
        else:
            await interaction.response.send_message("Rien à mettre en pause.", ephemeral=True)

    @app_commands.command(name="stop", description="Arrêter la musique")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client:
            voice_client.stop()
            await voice_client.disconnect()
            self.queue = asyncio.Queue()
            await interaction.response.send_message("🛑 Lecture stoppée")

    @app_commands.command(name="skip", description="Passer au titre suivant")
    async def skip(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            await interaction.response.send_message("⏭️ Titre suivant")
        else:
            await interaction.response.send_message("Rien à passer.", ephemeral=True)

    @app_commands.command(name="queue", description="Voir la file d'attente")
    async def show_queue(self, interaction: discord.Interaction):
        items = list(self.queue._queue)
        if not items:
            await interaction.response.send_message("File vide.")
            return
        description = "\n".join(f"{idx+1}. {track.title} - demandé par {track.requester.display_name}" for idx, track in enumerate(items))
        embed = discord.Embed(title="File d'attente", description=description)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Titre en cours")
    async def nowplaying(self, interaction: discord.Interaction):
        if not self.current:
            await interaction.response.send_message("Aucune lecture en cours.")
            return
        embed = discord.Embed(title="En cours", description=self.current.title)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="lyrics", description="Afficher les paroles")
    async def lyrics(self, interaction: discord.Interaction, query: str):
        lyrics = await fetch_lyrics(query)
        embed = discord.Embed(title=f"Paroles pour {query}", description=lyrics[:4000])
        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(MusicCog(bot, bot.config.music))
