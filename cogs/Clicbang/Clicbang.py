import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from utils.embed import new_embed
from utils import data
from .view import *
import asyncio


class Clicbang(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot


    @commands.slash_command(
        description = "Démarrer une partie de bang"
    )
    async def bang(self, inter : ApplicationCommandInteraction):
        menu = BangMenu(inter)
        await inter.response.send_message(
            embed = menu.embed,
            view = menu
        )
        await menu.wait()
        if menu.start:
            pass
        else:
            await menu.interaction.delete_original_message()
  
            
def setup(bot):
    bot.add_cog(Clicbang(bot))