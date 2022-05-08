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


#TODO (RIP TON APREM BRO)
    
        
        
    
               

def setup(bot):
    bot.add_cog(Clicbang(bot))