from typing import List, Tuple
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot

from modules.FastSnake import ButtonChoice

from modules.FastSnake import QCM, confirmation
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
            description="Création du tournoi annulé.", footer_text="Tu peux rejeter cemessage pour le faire disparaître.")

        phases: List[Tuple[int, int]] = []

        groupe_choice = [ButtonChoice(label=str(i+1)) for i in range(4)]
        size_choice = [ButtonChoice(label=str(i)) for i in [4, 5, 8]]

        for phase_idx in range(taille):
            title = f"Phase {FS.Emotes.Num(phase_idx+1)}"
            groups = await QCM(target=inter, choices=groupe_choice, pre_selection=groupe_choice[0], title=title, description="Nombre de groupe ?")
            if groups:
                size = await QCM(target=inter, choices=size_choice, pre_selection=size_choice[0], title=title, description="Taille des groupes ?")
                if size:
                    phases.append((int(groups.label), int(size.label)))
                else:
                    await inter.edit_original_message(embed=cancel_embed, view=None)
                    return
            else:
                await inter.edit_original_message(embed=cancel_embed, view=None)
                return
        title = "Création du tournoi"
        confirm = await confirmation(
            target=inter, 
            embeds=[
                FS.Embed(
                    title=title,
                    description="\n".join([f"__**Phases {i+1}**___\nNombre de groupe : {phase[0]}\nTaille des groupe : {phase[1]}" for i, phase in enumerate(phases)])
                )
            ], 
            title=title,
            description="Confirmer la configuration ?")
        if confirm:
            await inter.edit_original_message(embed=FS.Embed(title=title, description="Création des phases en cours..."), view=None)
            for i, phase in enumerate(phases):
                if phase[0] == 1:
                    new_tournoi = Tournament2v2Roll(
                        inter.guild, size=phase[1], name=f"PHASE {i+1}")
                    await new_tournoi.build()
                else:
                    for j in range(phase[0]):
                        new_tournoi = Tournament2v2Roll(
                            inter.guild, size=phase[1], name=f"PHASE {i+1} - GROUPE {chr(ord('A') +j)}")
                        await new_tournoi.build()
            await inter.edit_original_message(embed=FS.Embed(title=title, description="Phases créées !", footer_text="Tu peux rejeter ce message pour le faire disparaitre."))

        else:
            await inter.edit_original_message(embed=cancel_embed, view=None)


def setup(bot: InteractionBot):
    bot.add_cog(Tournament(bot))
