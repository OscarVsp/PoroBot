import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
import modules.FastSnake as FS
from .view import *
from .classes import *
import asyncio
from typing import List





class Tournament(commands.Cog):
    
    
    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot : InteractionBot = bot
        self.bot.tournaments_name : List[str] = []
        
    @commands.slash_command(name="tournament",     
        default_member_permissions=disnake.Permissions.all(),
        dm_permission=False
    )
    async def tournament(self, inter):
        pass
    
    
    @tournament.sub_command(
        name="new"
    )
    async def new_tournament(self, inter : ApplicationCommandInteraction,
                             nom : str = commands.Param(description="Nom du tournoi"),
                             description : str = commands.Param(description="Description du tournoi",default=None),
                             banniere : str = commands.Param(description="""Le lien "https" de l'image à utiliser comme bannière""", default = FS.Images.Tournament.ClashBanner),
                             participants : str = commands.Param(description="Filtrer les membres à afficher par un role ou un évenement.", default=None)
                        ):

        filtre_members : List[disnake.Member] = None
                
        if participants:
            filtre_clean = participants.split(' ')[1]
            for role in inter.guild.roles:
                if role.name == filtre_clean:
                    filtre_members = role.members
                    break
            
            if filtre_members == None:       
                for event in inter.guild.scheduled_events:
                    if event.name == filtre_clean:
                        filtre_members = [member async for member in event.fetch_users()]
                        break
            
            if filtre_members == None:
                filtre_members = inter.guild.members
    
        title = "Création du tournoi"
        selection = await FS.memberSelection(inter, title=title, message= "Sélectionne les membres participant au tournois.", pre_selection=filtre_members)
        if selection:
            new_role = await inter.guild.create_role(name=f"tournoi {nom}")
            for member in selection.members:
                await member.add_roles(new_role)
            await asyncio.sleep(1)
            tournament = TournamentView(inter,self,new_role,name=nom,description=description,banner=banniere)
            await inter.edit_original_message(
                embed = tournament.tournament.embed,
                view = tournament
            )
        else:
            await inter.edit_original_message(embed=FS.Embed(title=title,description=f":o: Création du tournoi annulée"), view=None)
        
        
    @new_tournament.autocomplete("participants")
    def autocomple_filtre(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        filtres = []
        for role in inter.guild.roles:
                if role.name.lower().startswith(user_input.lower()):
                        filtres.append(f"👥 {role.name}")
        for event in inter.guild.scheduled_events:
                if event.name.lower().startswith(user_input.lower()):
                        filtres.append(f"📅 {event.name}")
        if len(filtres) > 25:
            filtres = filtres[:25]
        return filtres
    
    
    

def setup(bot):
    bot.add_cog(Tournament(bot))