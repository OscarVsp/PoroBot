import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from random import randint,choices,sample
from utils.FastEmbed import FastEmbed
from utils.data import emotes, color
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
        default_member_permissions=disnake.Permissions.all())
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
                                role : disnake.Role = commands.Param(description="Role contenant les participants"),
                                name : str = commands.Param(description="Nom du tournoi", default="Tournoi"),
                                order : str = commands.Param(description="Liste des IDs des joueurs dans l'ordre à utiliser", default="Random")):
        """Create a tournament 2v2 roll of 4, 5 or 8 players
        """
        if len(role.members) not in [4,5,8]:
            await inter.response.send_message(
                embed = FastEmbed(
                    description=f"Ce type de tournois nécessite 4, 5 ou 8 joueurs, mais le role spécifié ({role.name}) ne contient que {len(role.members)} membres.",
                    color = color.rouge,
                    ), ephemeral = True)
            return 
        if order == "Random":
            members = role.members
            ordered = False 
        else:
            ids = order.split(',')
            if len(ids) != len(role.members):
                await inter.response.send_message(
                    embed = FastEmbed(
                        description=f"Nombre d'IDs donnés ({len(ids)}) est différent du nombre de membre ({len(role.members)}) ayant le rôle {role.name}.",
                        color = color.rouge,
                        ), ephemeral = True)
                return  
            ordered_members = []
            for id in ids:
                member = next((m for m in role.members if m.id == int(id)), None)
                if member == None:
                    await inter.response.send_message(
                        embed = FastEmbed(
                            description=f"L'ID {id} ne correspond à aucun des membres dans le role {role.name}.",
                            color = color.rouge,
                            ), ephemeral = True)
                    return 
                ordered_members.append(member)
            members = ordered_members 
            ordered = True            
        await inter.response.defer(ephemeral=True)
        self.bot.tournaments_name += [name]
        await self.bot.change_presence(activity = disnake.Activity(name=", ".join(self.bot.tournaments_name), type=disnake.ActivityType.playing))       
        new_tournament = Tournament2v2RollView(inter, self.bot, role, members, ordered, name)
        await new_tournament.makeChannels()
        await inter.edit_original_message(
            embed = FastEmbed(description=f"Tournois {name} créé.\n[Dashboard]({new_tournament.channel_dashboard.jump_url})")
        )
        
    
        
    #command to create a new tournament
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
            embed = FastEmbed(description=f"Tournois {new_tournament.name} créé.\n[Dashboard]({new_tournament.channel_dashboard.jump_url})")
        )
        
    

def setup(bot):
    bot.add_cog(Tournament(bot))