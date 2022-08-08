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
    
    @tournament.sub_command_group(
        name="2v2_roll"
    )
    async def tournamant2v2Roll(self, inter):
        pass
        
    

    #command to create a new tournament
    @tournamant2v2Roll.sub_command(
        name="new", description="Créer un tournois 2v2 roll de 4, 5 ou 8 joueurs"
    )
    async def newTournament2v2Roll(self, inter: ApplicationCommandInteraction,
                                name : str = commands.Param(description="Nom du tournoi", default="Tournoi"),
                                annonce : str = commands.Param(description="Le text à inclure dans l'annonce initial du tournoi", default=None),
                                role : disnake.Role = commands.Param(description="Un role depuis lequel importer des joureurs", default = None),
                                event : str = commands.Param(description="Un évent depuis lequel importer des joueurs", default = None),
                                banniere : str = commands.Param(description="""Le lien "https" de l'image à utiliser comme bannière""", default = FS.Images.Tournament.ClashBanner)):
        """Create a tournament 2v2 roll of 4, 5 or 8 players
        """
        await inter.response.defer(ephemeral=True)
        members : list[disnake.Member] = []
        if role:
            members += role.members
        if event:
            async for member in event.fetch_users():
                if member not in members:
                    members.append(member)
        selection = await FS.memberSelection(inter, title="Sélection des joueurs.", message= "Sélectionne les membres participant au tournois.", size = [4,5,8], pre_selection=members)
        if selection.is_confirmed:
            await inter.edit_original_message(
                embed = FS.Embed(description=f"⌛ Création du tournois {name} en cours..."),
                view=None
            )
            self.bot.tournaments_name += [name]
            await self.bot.change_presence(activity = disnake.Activity(name=", ".join(self.bot.tournaments_name), type=disnake.ActivityType.playing)) 
            tournament_role = await inter.guild.create_role(name=f"Tournament {name} role")
            for member in selection.members:
                await member.add_roles(tournament_role, reason=f"Tournement {name}")    
            await asyncio.sleep(2)
            new_tournament = Tournament2v2RollView(inter, self.bot, tournament_role, name = name, banner = banniere, annonce = annonce)
            await new_tournament.makeChannels()
            await inter.edit_original_message(
                embed = FS.Embed(description=f"Tournois {name} créé.\n[Dashboard]({new_tournament.channel_dashboard.jump_url})")
            )
        else:
            await inter.edit_original_message(embed=FS.Embed(description=f"Création du tournois annulée"), view=None)
        
    @newTournament2v2Roll.autocomplete("event")
    async def autocomp_event_export(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        events = []
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                events.append(event.name)
        return events    
    
        
    #command to load a tournament
    @tournamant2v2Roll.sub_command(
        name="load", description="Load un tournois 2v2 roll de 4, 5 ou 8 joueurs"
    )
    async def loadTournament2v2Roll(self, inter: ApplicationCommandInteraction,
                                file : disnake.Attachment = commands.Param(description="Le fichier .json depuis lequel load le tournois.")):
        """Load a tournament 2v2 roll of 4, 5 or 8 players
        """
        await inter.response.defer(ephemeral=True)  
        file = await file.to_file()          
        new_tournament : Tournament2v2RollView = await Tournament2v2RollView.load_from_save(inter, file)
        self.bot.tournaments_name += [new_tournament.name]
        await self.bot.change_presence(activity = disnake.Activity(name=", ".join(self.bot.tournaments_name), type=disnake.ActivityType.playing))       
        await inter.edit_original_message(
            embed = FS.Embed(description=f"Tournois {new_tournament.name} créé.\n[Dashboard]({new_tournament.channel_dashboard.jump_url})")
        )
        
    

def setup(bot):
    bot.add_cog(Tournament(bot))