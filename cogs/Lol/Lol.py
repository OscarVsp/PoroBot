from typing import List, Tuple
from urllib import response
import pickledb
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from modules.FastSnake.SimpleModal import SimpleModal
from modules.FastSnake.Views import confirmation, memberSelection
from .view import *
from .watcher import Summoner, Watcher
from .exceptions import *




class Lol(commands.Cog):
    
        def __init__(self, bot):
                """Initialize a Lol cog object and laod the lore of the members.

                Get the member dict for the lore from the "Members.json" file next to it.
                """
                self.bot : commands.InteractionBot = bot
                self.watcher : Watcher = Watcher(bot.config["RIOT_APIKEY"],"euw1")
                self.summoners = pickledb.load("cogs/Lol/summoners.db", False)

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
                except (SummonerNotFound):
                        await inter.edit_original_message(
                                embed = FS.Embed(
                                        title = f"__**Clash**__",
                                        description = f"**{summoner}** n'a pas pu être trouvé...\nVérifiez que le nom d'invocateur soit correct.",
                                        thumbnail = FS.Images.Poros.Question
                                )
                        )
                        
        @commands.slash_command(
                name="lol"
        )                
        async def lol(self, inter):
                pass
        
        async def set_summoner(self, inter : ApplicationCommandInteraction, target : disnake.User, invocateur : str):

                if str(target.id) in self.summoners.getall():
                        confirm = await confirmation(inter,title="Invocateur déjà existant",message=("Tu as" if target == inter.author else f"{target.mention} a")+f" déjà le nom d'invocateur suivant enregistré : ***{self.summoners.get(str(target.id))}***\n Veux-tu le remplacer ?",timeout=120)
                        if not confirm:
                                await inter.edit_original_message(embed=FS.Embed(title="Invocteur déjà existant",description="Nom d'invocateur non changé",footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
                                return
                try:
                        summoner = await self.watcher.get_summoner_by_name(invocateur)
                except SummonerNotFound:
                        await inter.edit_original_message(embed=FS.Embed(title="Invocateur inconnu",description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...",footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view = None)
                        return
                        
                confirm = await confirmation(inter, title="Valider l'invocateur", message=f"__**{summoner.name}**__\n__Level :__ **{summoner.level}**", thumbnail=summoner.icon)
                
                if not confirm:
                        await inter.edit_original_message(embed=FS.Embed(title="Invocteur déjà existant",description="Nom d'invocateur non changé",footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
                        return
                self.summoners.set(str(target.id), invocateur)
                self.summoners.dump()
                await inter.edit_original_message(embed=FS.Embed(title="Invocateur enregistré", description=f"L'invocateur ***{invocateur}*** à bien été lié avec " + ("ton compte discord !" if inter.author == target else f"le compte discord de {target.mention}"), footer_text="Tu peux rejeter ce message pour le faire disparaitre."), view=None)
        
        @lol.sub_command(
                description="Lier son compte discord avec son compte League of Legends"
        )
        async def account(self, inter : ApplicationCommandInteraction,
                          invocateur : str = commands.Param(description="Ton nom d'invocateur sur League of Legends")):
                await inter.response.defer(ephemeral=True)
                await self.set_summoner(inter, inter.author, invocateur)
                
        async def modal_callback(self, interaction : disnake.ModalInteraction, answers : dict, callback_datas : dict):
                await self.set_summoner(interaction, callback_datas.get('target'), answers.get("summoner_name"))
                        
                
        @commands.user_command(
                name="Nom d'invocateur"
        )
        async def summoner_set(self, inter : ApplicationCommandInteraction, target : disnake.User):
                await inter.response.send_modal(SimpleModal(f"Définir le nom d'invocateur de {target.display_name}", questions=[disnake.ui.TextInput(label="Nom d'invocateur", custom_id="summoner_name")], callback = self.modal_callback, callback_datas={'target':target}))



        @lol.sub_command(
                name="classement"
        )
        async def classement(self, inter : ApplicationCommandInteraction):
                await inter.response.defer(ephemeral=True)
                members : List[disnake.Member] = []
                summoners : List[Summoner] = []
                for user_id_str in self.summoners.getall():
                        member = inter.guild.get_member(int(user_id_str))
                        if member:
                                summoners.append(await self.watcher.get_summoner_by_name(self.summoners.get(user_id_str)))
                                members.append(member)
                
                sorted_summoners : List[Summoner] = sorted(summoners, key=lambda x:x.classement)
                sorted_members : List[disnake.Member] = []
                
                for summoner in sorted_summoners:
                        sorted_members.append(members[summoners.index(summoner)])

                await inter.edit_original_message(embed = FS.Embed(
                        title=f"{FS.Assets.Emotes.lol} __**CLASSEMENT LEAGUE OF LEGENDS**__",
                        description="\n".join([ f"{sorted_summoners[i].tier_emote} **{sorted_summoners[i].rank}** __**{sorted_members[i].display_name}**__"  for i in range(len(sorted_members))])
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