import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from .view import *
from .watcher import Watcher
from .exceptions import *




class Lol(commands.Cog):
    
        def __init__(self, bot):
                """Initialize a Lol cog object and laod the lore of the members.

                Get the member dict for the lore from the "Members.json" file next to it.
                """
                self.bot : commands.InteractionBot = bot
                self.watcher : Watcher = Watcher(bot.config["RIOT_APIKEY"],"euw1")

        @commands.slash_command(
                description = "Scouter une team clash à partir du nom d'un des joueurs"
        )
        async def clash(self, inter: ApplicationCommandInteraction,
                        summoner : str = commands.Param(
                                description = "Le nom d'invocateur d'un des joueurs"
                        )
                ):
                await inter.response.defer()
                try:
                        team = await self.watcher.get_clash_team(summoner)
                        await inter.edit_original_message(
                                embed= team.embed,
                                components = disnake.ui.Button(label="OPGG", emoji= FS.Emotes.OPGG, style = disnake.ButtonStyle.link, url = team.opgg)
                        )
                except (NoCurrentTeam):
                        await inter.edit_original_message(
                                embed = FS.Embed(
                                        title = f"__**Clash**__",
                                        description = f"**{summoner}** ne fait pas parti d'une équipe clash actuellement...",
                                        thumbnail = FS.Images.Poros.Question
                                )
                        )
                except (SumomnerNotFound):
                        await inter.edit_original_message(
                                embed = FS.Embed(
                                        title = f"__**Clash**__",
                                        description = f"**{summoner}** n'a pas pu être trouvé...\nVérifiez que le nom d'invocateur soit correct.",
                                        thumbnail = FS.Images.Poros.Question
                                )
                        )
        
        @commands.slash_command(
                description = "Voir combien de temps et d'argent tu as dépensés sur LOL"
        )
        async def wasteonlol(self, inter : ApplicationCommandInteraction):
                await inter.response.send_message(
                        embed = FS.Embed(
                                title = "__**Wasted on Lol**__",
                                description = "Utilise les liens ci-dessous pour découvrir combien de temps et/ou d'argent tu as dépensés dans League of Legends",
                                thumbnail = FS.Images.Poros.Neutral
                        
                        ),
                        components = [
                                disnake.ui.Button(label="Temps passé sur lol", emoji= "⌛", style = disnake.ButtonStyle.link, url = "https://wol.gg/"),
                                disnake.ui.Button(label="Argent dépensé sur lol", emoji= "💰", style = disnake.ButtonStyle.link, url = "https://support-leagueoflegends.riotgames.com/hc/fr/articles/360026080634")
                        ],
                        delete_after = 60
                )
                
        @commands.slash_command(
                description = "Obtenir les règles de l'aram à boire"
        )
        async def drink(self, inter : ApplicationCommandInteraction):
                await inter.response.send_message(embed = drink_embed)
                
        @commands.slash_command(
                description = "Obtenir le dernier patch the League of Legends"
        )
        async def patchnote(self, inter : ApplicationCommandInteraction,
                previous : int = commands.Param(
                        description = "Nombre de patch en arrière (0 pour le patch en cours)",
                        ge = 0,
                        default = 0
                )
        ):
                patch = PatchNoteView(inter, previous)
                await inter.response.send_message(
                        embed = patch.embed,
                        view = patch
                )
                
                
                       


def setup(bot : commands.InteractionBot):
    bot.add_cog(Lol(bot))