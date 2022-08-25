import os
import disnake
from disnake.ext import commands, tasks
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from .view import *
from .scraper import Almanax_scraper
import asyncio
import logging
from datetime import datetime
import asyncpg


class Dofus(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: commands.InteractionBot = bot
        self.scraper = Almanax_scraper()
        self.almanax_message: disnake.Message = None
        self.almanax_task.add_exception_type(asyncpg.PostgresConnectionError)
        self.almanax_task.start()

    @commands.slash_command(description="Obtenir l'almanax du jour/des prochains jours")
    async def almanax(
        self,
        inter: ApplicationCommandInteraction,
        nombre_de_jours: int = commands.Param(
            description="Le nombre de prochain jour dont tu veux connaitre l'almanax", ge=0, default=0
        ),
    ):
        await inter.response.send_message(
            embed=FS.Embed(
                title="Consultation du Krosmoz en cours...",
                description="À chaque fois que l'almanax d'un jour est demandé pour la première fois, cela peut prendre un peu de temps.\nL'almanax te sera envoyé en privé dès qu'il sera prêt.",
                thumbnail=FS.Images.SABLIER,
            ),
            delete_after=10,
        )
        embed_s = AlmanaxView.data_to_embed(await Almanax_scraper.get_almanax(nombre_de_jours))
        if type(embed_s) == list:
            for embed in embed_s:
                await inter.author.send(embed=embed)
        else:
            await inter.author.send(embed=embed_s)

    @tasks.loop(hours=24)
    async def almanax_task(self):
        logging.info("Almanax tasks run")
        await self.almanax_message.delete()
        self.almanax_message = await self.almanax_channel.send(
            embed=AlmanaxView.data_to_embed(await Almanax_scraper.get_almanax())
        )

    @almanax_task.before_loop
    async def before_almanax_task(self):
        if bool(os.getenv("TEST")):
            self.almanax_task.cancel()
            logging.info("Almanax task skipped because test mod")
        else:
            logging.info("Almanax task waiting for bot to be ready...")
            await self.bot.wait_until_ready()
            await asyncio.sleep(1)
            self.almanax_channel = self.bot.get_channel(int(self.bot.config["ALMANAX_CHANNEL"]))
            if self.almanax_channel == None:
                self.almanax_task.cancel()
                logging.error(f"Almanax channel '{self.almanax_channel}' not found. Task is cancelled.")
            else:
                await self.almanax_channel.purge(limit=10)
                self.almanax_message = await self.almanax_channel.send(
                    embed=AlmanaxView.data_to_embed(await Almanax_scraper.get_almanax())
                )
                logging.info("Almanax first tasks run at start.")
                time = datetime.now()
                time_to_wait = (23 - time.hour) * 3600 + (59 - time.minute + 1) * 60 + (59 - time.second)
                logging.info(
                    f"Almanax tasks waiting for {(23-time.hour)} hours, {(59-time.minute+1)} minutes and {(59-time.second)} secondes before next task"
                )
                await asyncio.sleep(time_to_wait)

    @almanax_task.error
    async def error_almanax_task(self, error):
        tb = self.bot.tracebackEx(error)
        await self.bot.log_channel.send(
            embed=FS.Embed(
                title=f":x: __** ERROR**__ :x:", description=f"""```{error}```\nRaised on task **Almanax_task**."""
            )
        )
        n = len(tb) // 4096
        for i in range(n):
            await self.bot.log_channel.send(embed=FS.Embed(description=f"```python\n{tb[4096*i:4096*(i+1)]}```"))
        await self.bot.log_channel.send(embed=FS.Embed(description=f"```python\n{tb[4096*n:]}```"))
        logging.error(f"{error} raised on task Almanax_task \n {tb}")

    def cog_unload(self):
        self.almanax.cancel()


def setup(bot: commands.InteractionBot):
    bot.add_cog(Dofus(bot))
