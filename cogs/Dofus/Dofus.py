import disnake
from disnake.ext import commands,tasks
from disnake import ApplicationCommandInteraction
from requests import delete
from utils.embed import new_embed
from utils import data
from .view import *
from .scraper import Almanax_scraper
import asyncio
import logging
from datetime import datetime


class Dofus(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot
        self.scraper = Almanax_scraper()
        self.almanax_message = None
        self.almanax_task.start()
        
    @commands.slash_command(
        description = "Obtenir l'almanax du jour/des prochains jours"
    )
    async def almanax(self, inter : ApplicationCommandInteraction,
        nombre_de_jours : int = commands.Param(
            description = "Le nombre de prochain jour dont tu veux connaitre l'almanax",
            ge = 0,
            le = 30,
            default = 0
        )
    ):
        await inter.response.send_message(
            embed = new_embed(
                description = "Consultation du Krosmoz en cours...\nL'almanax vous sera envoyé en privé dès qu'il sera prêt.",
            ),
            delete_after = 10
        )
        await inter.author.send(
            embed = AlmanaxView.data_to_embed(Almanax_scraper.scrape(nombre_de_jours))
        )
        


    @tasks.loop(hours=24)
    async def almanax_task(self):
        logging.info("Almanax tasks run")
        await self.almanax_message.delete()
        self.almanax_message = await self.almanax_channel.send(AlmanaxView.data_to_embed(Almanax_scraper.scrape()))

    @almanax_task.before_loop
    async def before_almanax_task(self):
        logging.info("Almanax task waiting for bot to be ready...")
        await self.bot.wait_until_ready()
        await asyncio.sleep(1)
        self.almanax_channel = self.bot.get_channel(int(self.bot.config['ALMANAX_CHANNEL']))
        if self.almanax_channel == None:
            logging.error("Almanax channel not found")
            self.almanax.cancel()
        else:
            await self.almanax_channel.purge(limit=10)
            self.almanax_message = await self.almanax_channel.send(embed = AlmanaxView.data_to_embed(Almanax_scraper.scrape()))
            logging.info("Almanax before tasks run at start.")
            time = datetime.now()
            time_to_wait = (23-time.hour)*3600 + (59-time.minute+1)*60 + (59-time.second)
            logging.info(f"Almanax tasks waiting for {(23-time.hour)} hours, {(59-time.minute+1)} minutes and {(59-time.second)} secondes before starting task")
            await asyncio.sleep(time_to_wait)
    
        
        
    def cog_unload(self):
        self.almanax.cancel()

def setup(bot):
    bot.add_cog(Dofus(bot))