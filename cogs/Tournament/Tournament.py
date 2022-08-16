from typing import List
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from .classes import TournamentData

from modules.FastSnake import confirmation
from modules.FastSnake.ChoicesView import SelectionRow
from modules.FastSnake.Views import Selection
from .TournamentManager import Tournament2v2Roll
import modules.FastSnake as FS


class Tournament(commands.Cog):

    def __init__(self, bot):
        """Initialize the cog
        """
        self.bot: InteractionBot = bot

    @commands.slash_command(name="tournament",
                            default_member_permissions=disnake.Permissions.all(),
                            dm_permission=False
                            )
    async def tournament(self, inter):
        pass

    @tournament.sub_command(
        name="roll2v2",
        description="Créer un tournoi en format 2v2 roll"
    )
    async def roll2v2(self, inter: ApplicationCommandInteraction,
                      nom: str = commands.Param(description="Nom du tournoi"),
                      taille: int = commands.Param(
                          description="Nombre de participants", choices=[4, 5, 8])
                      ):

        await inter.response.defer(ephemeral=True)
        tournament = Tournament2v2Roll(inter.guild, taille, name=nom)
        await tournament.build()
        await inter.edit_original_message(embed=FS.Embed(description=f"Tournois [{tournament.name}]({tournament.admin_message.jump_url}) créé !"))

    @tournament.sub_command(
        name="mulit",
        description="Créer un tournoi à plusieurs phases"
    )
    async def multi(self, inter: ApplicationCommandInteraction,
                    taille: int = commands.Param(description="Nombre de phases", gt=0)):
        await inter.response.defer(ephemeral=True)
        cancel_embed: disnake.Embed = FS.Embed(
            description="Création du tournoi annulé.", footer_text="Tu peux rejeter ce message pour le faire disparaître.")

        phases: List[List[TournamentData]] = []
        
        def embeds(phases):
            return [
                FS.Embed(
                    title="🏆 __**TOURNOI CRÉATION**__ 🏆",
                    description="\n\n".join([f"{FS.Assets.Emotes.bracket} __**Phases {i+1}**___\nNombre de groupe : {len(phase)}\nTaille des groupe : {phase[0].size}" for i, phase in enumerate(phases)])
                )
            ]
            
        
       
        
        for phase_idx in range(taille):
            title = f"{FS.Assets.Emotes.bracket} Phase {FS.Emotes.Num(phase_idx+1)}"
            
            phaseSelection = await Selection(inter,[SelectionRow("Nombre de groupe",[str(i+1) for i in range(20)],max_values=1),SelectionRow("Type de phase",["2V2 Roll"],max_values=1)],title=title,embeds=embeds(phases))
            if phaseSelection:
                if phaseSelection.responses[1] == ["2V2 Roll"]:
                    sizeSelection = await Selection(inter,[SelectionRow("Taille des groupes",["4","5","8"],max_values=1)],title=title,embeds=embeds(phases))
                    if sizeSelection:
                        phases.append([Tournament2v2Roll(inter.guild,int(sizeSelection.responses[0][0]),name=f"PHASE {phase_idx+1} - GROUPE {chr(ord('A') +j)}") for j in range(int(phaseSelection.responses[0][0]))])
                    else:
                        await inter.edit_original_message(embed=cancel_embed, view=None)
                        return
            else:
                await inter.edit_original_message(embed=cancel_embed, view=None)
                return
        
        
        title = "Validation"
        confirm = await confirmation(
            target=inter, 
            embeds=embeds(phases), 
            title=title,
            description="Confirmer la configuration ?")
        if confirm:
            await inter.edit_original_message(embed=FS.Embed(title=title, description="Création des phases en cours..."), view=None)
            for phase in phases:
                for group in phase:
                    await group.build()
            await inter.edit_original_message(embed=FS.Embed(title=title, description="Phases créées !", footer_text="Tu peux rejeter ce message pour le faire disparaitre."))

        else:
            await inter.edit_original_message(embed=cancel_embed, view=None)


def setup(bot: InteractionBot):
    bot.add_cog(Tournament(bot))
