# -*- coding: utf-8 -*-
from random import choice

import asyncpg
import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from disnake.ext import tasks

import modules.FastSnake as FS
from .view import *
from bot.bot import Bot


class Basic(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot
        self.presence_update.add_exception_type(asyncpg.PostgresConnectionError)
        self.presence_update.start()

    @commands.slash_command(description="Commander un bière (test le ping du bot)")
    async def beer(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(
                title="Voilà tes bières",
                description=f":beer:\n Après {round(self.bot.latency,2)} secondes d'attente seulement !",
                color=disnake.Colour.gold(),
            ),
            view=Beer(inter),
        )

    @commands.slash_command(description="Nourrir le poro avec des porosnacks jusqu'à le faire exploser")
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(description="Nourris le poro !", image=FS.Images.Poros.POROGROWINGS[0], footer_text="0/10"),
            view=PoroFeed(inter),
        )

    @commands.slash_command(description="Démarrer watch together dans un salon vocal")
    async def watch_together(self, inter: ApplicationCommandInteraction):
        if inter.author.voice and inter.author.voice.channel and inter.author.voice.channel.guild == inter.guild:
            invite = await inter.author.voice.channel.create_invite(
                max_age=0,
                target_type=disnake.InviteTarget.embedded_application,
                target_application=disnake.PartyType.watch_together,
            )
            button = disnake.ui.Button(
                style=disnake.ButtonStyle.link, url=f"https://discord.gg/{invite.code}", label="Watch together"
            )
            await inter.response.send_message(
                embed=FS.Embed(
                    description=f"Cliquez ci-dessous pour démarrer watch together dans le channel vocal **{inter.author.voice.channel.name}**"
                ),
                components=[button],
                ephemeral=True,
            )
        else:
            await inter.response.send_message(
                embed=FS.Embed(
                    description=f"Vous devez etre dans un salon vocal de ce serveur pour commencer watch together.",
                    ephemeral=True,
                )
            )

    @commands.user_command(name="Voir le lore")
    async def lore(self, inter: disnake.UserCommandInteraction):
        lore_embed = get_lore_embed(inter.target.name)
        if lore_embed == False:
            await inter.response.send_message(
                embed=FS.Embed(
                    description=f"{inter.target.name} n'a pas encore de lore...\nDemande à Hyksos de l'écrire !",
                    thumbnail=FS.Images.Poros.SWEAT,
                ),
                ephemeral=True,
            )
        else:
            await inter.response.send_message(embed=lore_embed, delete_after=60 * 5)

    @commands.user_command(name="Créer / éditer le lore", default_member_permissions=disnake.Permissions.all())
    async def addlore(self, inter: disnake.UserCommandInteraction):
        if inter.author.id == 187886815666110465 or inter.author == self.bot.owner:
            await inter.response.send_modal(modal=loreModal(self.bot, inter.target))
        else:
            await inter.response.send_message(
                embed=FS.warning("Seul Hyksos peut utiliser cette commande !"), ephemeral=True
            )

    @tasks.loop(seconds=30)
    async def presence_update(self):
        cmd: disnake.APISlashCommand = choice(self.list_slash_cmd)

        await self.bot.change_presence(
            activity=disnake.Activity(
                name=f"/{cmd.name}" + (f" {choice(cmd.options).name}" if cmd.options else ""),
                type=disnake.ActivityType.watching,
            )
        )

    @presence_update.before_loop
    async def presence_update_before(self):
        await self.bot.wait_until_ready()
        self.list_slash_cmd = []
        for cmd in list(self.bot.global_slash_commands):
            if not cmd.default_member_permissions:
                self.list_slash_cmd.append(cmd)
        if len(self.list_slash_cmd) == 0:
            self.presence_update.cancel()

    @presence_update.error
    async def presence_update_error(self, error):
        tb = self.bot.tracebackEx(error)
        await self.bot.log_channel.send(
            embed=FS.Embed(
                title=f":x: __** ERROR**__ :x:",
                description=f"""```{error}```\nRaised on task **presence_update task**.""",
            )
        )
        n = len(tb) // 4096
        for i in range(n):
            await self.bot.log_channel.send(embed=FS.Embed(description=f"```python\n{tb[4096*i:4096*(i+1)]}```"))
        await self.bot.log_channel.send(embed=FS.Embed(description=f"```python\n{tb[4096*n:]}```"))
        logging.error(f"{error} raised on task presence_update\n {tb}")

    def cog_unload(self):
        self.presence_update.cancel()


def setup(bot: commands.InteractionBot):
    bot.add_cog(Basic(bot))
