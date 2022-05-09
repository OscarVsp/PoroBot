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
        menu = BangMenu(inter.author)
        await menu.update(inter)
        timeout = await menu.wait()
        if not timeout and not menu.cancelled:
            game = BangGame(menu.players)
            await game.start_game(menu.interaction)
            
  
            
def setup(bot):
    bot.add_cog(Clicbang(bot))