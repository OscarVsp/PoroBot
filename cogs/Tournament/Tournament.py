from ast import Param
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.FastEmbed import FastEmbed
from utils.data import emotes
from .view import *
from .classes import *
import asyncio



class Tournament(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot = bot
        self.addPlayer = None
        
    @commands.slash_command(name="tournament",     
        default_member_permissions=disnake.Permissions.all())
    async def tournament(self, inter):
        pass
    

    #command to create a new tournament
    @tournament.sub_command(
        name="2v2_roll", description="Create a tournament 2v2 roll of 4, 5 or 8 players"
    )
    async def tournament2v2Roll(self, inter: ApplicationCommandInteraction, 
                                 participants : disnake.Role = commands.Param(description="Role des participants"),
                                 name : str = commands.Param(description="Nom du tournoi", default="Tournoi")):
        """Create a tournament 2v2 roll of 4, 5 or 8 players
        """
        if len(participants.members) not in [4,5,8]:
            await inter.response.send_message(
                embed = FastEmbed(
                    description=f"This tournament requires 4,5 or 8 players but {len(participants.members)} players are in the role {participants.name}.",
                    ), ephemeral = True)
            return 
        await inter.response.defer()
        await self.bot.change_presence(activity = disnake.Activity(name=name, type=disnake.ActivityType.playing))       
        new_tournament = Tournament2v2RollView(inter, self.bot, participants, name)
        await new_tournament.makeChannels()
        await inter.edit_original_message(
            embed = FastEmbed(description=f"Tournament {name} created.")
        )
        await asyncio.sleep(5)
        await inter.delete_original_message()
        
    

def setup(bot):
    bot.add_cog(Tournament(bot))