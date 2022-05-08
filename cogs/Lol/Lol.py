import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.embed import new_embed
from utils import data
from .view import *
import asyncio
from .watcher import ClashTeam,Watcher
from .exceptions import *


class Lol(commands.Cog):
    
        def __init__(self, bot):
                """Initialize a Lol cog object and laod the lore of the members.

                Get the member dict for the lore from the "Members.json" file next to it.
                """
                self.bot = bot
                self.watcher = Watcher(bot.config["RIOT_APIKEY"])

        @commands.slash_command()
        async def clash(self, inter: ApplicationCommandInteraction, sumonner : str):
                """Commander une bière (permet de tester le ping du bot)
                """
                try:
                        await inter.response.send_message(
                                embed=self.watcher.get_clash_team(sumonner).to_embed()
                        )
                except (NoCurrentTeam):
                        await inter.response.send_message(
                                embed = new_embed(
                                        description="Aucune équipe trouvée..."
                                )
                        )
                except (SumomnerNotFound):
                        await inter.response.send_message(
                                embed = new_embed(
                                        description = "Invocateur introuvable..." 
                                )
                        )
        
        @commands.slash_command()
        async def test(self, inter : ApplicationCommandInteraction):
                pass
                        


def setup(bot):
    bot.add_cog(Lol(bot))