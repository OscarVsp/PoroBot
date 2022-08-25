# -*- coding: utf-8 -*-
import logging
from typing import List

import disnake
from deep_translator import GoogleTranslator
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

import modules.FastSnake as FS
from .view import Locker


class Server(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: commands.InteractionBot = bot
        self.locked_channels: List[Locker] = []
        self.translator = GoogleTranslator(source="auto", target="en")

    @staticmethod
    def incoming_connection(before: disnake.VoiceState, after: disnake.VoiceState) -> bool:
        return after.channel != None and before.channel != after.channel

    @staticmethod
    def outgoing_connection(before: disnake.VoiceState, after: disnake.VoiceState) -> bool:
        return before.channel != None and before.channel != after.channel

    @commands.slash_command(
        name="lock",
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False,
        description="Verrouiller un channel vocal.",
    )
    async def lock(
        self,
        inter: ApplicationCommandInteraction,
        channel: str = commands.Param(description="Le channel vocal à verrouiller"),
        raison: str = commands.Param(
            description='La raison du verrouillage à préciser aux spectateurs (défaut : "Focus")', default="Focus"
        ),
    ):
        await inter.response.defer(ephemeral=True)
        for chan in inter.guild.voice_channels:
            if chan.name == channel:
                locked_channel = chan
                break
        if not locked_channel.permissions_for(inter.guild.default_role).speak:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=f"Le channel vocal doit initialement permettre au role {inter.guild.default_role.mention} de parler."
                )
            )
            return
        newLocker = Locker(inter, self, locked_channel, raison, timeout_on_no_participants=1)
        await newLocker.lock(inter)

    @lock.autocomplete("channel")
    async def autocomp_locked_chan(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        unlocked_channel = []
        for channel in inter.guild.voice_channels:
            if channel not in self.locked_channels:
                if channel.permissions_for(inter.author).view_channel:
                    unlocked_channel.append(channel.name)
        return unlocked_channel

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_update(self, member: disnake.Member, before: disnake.VoiceState, after: disnake.VoiceState):
        if self.incoming_connection(before, after):
            for locked_channel in self.locked_channels:
                if locked_channel == after.channel:
                    await locked_channel.incoming_connection(member)
        if self.outgoing_connection(before, after):
            for locked_channel in self.locked_channels:
                if locked_channel == before.channel:
                    await locked_channel.outgoing_connection(member)

    @commands.Cog.listener("on_ready")
    async def on_ready(self):
        channels_dirty_name: List[disnake.VoiceChannel] = []
        for guild in self.bot.guilds:
            for role in guild.roles:
                if role.name.endswith(Locker.role_name_authorized) or role.name.endswith(Locker.role_name_unauthorized):
                    await role.delete(reason=f"Cleaning old Locker")
                    logging.info(f'Role "{guild.name}:{role.name}" deleted by Locker cleaning')
                    channel_id: int = int(role.name.split(" ")[0])
                    channel = await self.bot.fetch_channel(channel_id)
                    if channel.name.startswith("🔒 ") and channel not in channels_dirty_name:
                        channels_dirty_name.append(channel)
        for channel in channels_dirty_name:
            await channel.edit(name=channel.name[2:], reason="Cleanning old Locker")
            logging.info(f'Channel "{guild.name}:{channel.name}" name cleaned to {channel.name[2:]} by Locker cleaning')

    def tr(self, text: str) -> str:
        if text != None and text != disnake.Embed.Empty:
            return_text = ""
            i = (0, 4999)
            while i[1] < len(text):
                tr_text = self.translator.translate(text[i[0] : i[1]])
                if tr_text:
                    return_text += tr_text
                else:
                    return_text += text[i[0] : i[1]]
                i[0] += 5000
                i[1] += 5000
            tr_text = self.translator.translate(text[i[0] :])
            if tr_text:
                return_text += tr_text
            else:
                return_text += text[i[0] :]
            return return_text
        else:
            return ""

    @commands.message_command(name="Translate")
    async def translate(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content = self.tr(inter.target.content)
        embeds = []
        if inter.target.embeds:
            for embed in inter.target.embeds:
                if embed.title != disnake.Embed.Empty:
                    embed.title = self.tr(embed.title)
                if embed.description != disnake.Embed.Empty:
                    embed.description = self.tr(embed.description)
                if embed.footer.text:
                    embed.set_footer(text=self.tr(embed.footer.text), icon_url=embed.footer.icon_url)
                if embed.author.name:
                    embed.set_author(
                        name=self.tr(embed.author.name), url=embed.author.url, icon_url=embed.author.icon_url
                    )
                fields = embed.fields.copy()
                embed.clear_fields()
                for field in fields:
                    embed.add_field(name=self.tr(field.name), value=self.tr(field.value), inline=field.inline)

                embeds.append(embed)
        await inter.edit_original_message(
            content=content,
            embeds=embeds,
        )


def setup(bot: commands.InteractionBot):
    bot.add_cog(Server(bot))
