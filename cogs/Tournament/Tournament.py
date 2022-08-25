from typing import List
import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot

from cogs.Tournament.TournamentMutliView import phaseCreation
from .classes import TournamentData

from modules.FastSnake import confirmation
from modules.FastSnake.ChoicesView import SelectionRow
from modules.FastSnake.Views import Selection
from .TournamentManager import Tournament2v2Roll
import modules.FastSnake as FS


class Tournament(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: InteractionBot = bot

    @commands.slash_command(
        name="tournament",
        default_member_permissions=disnake.Permissions.all(),
        guild_ids=[533360564878180382, 1008343697097760800],
        dm_permission=False,
    )
    async def tournament(self, inter):
        pass

    @tournament.sub_command(name="roll2v2", description="Créer un tournoi en format 2v2 roll")
    async def roll2v2(
        self,
        inter: ApplicationCommandInteraction,
        nom: str = commands.Param(description="Nom du tournoi"),
        taille: int = commands.Param(description="Nombre de participants", choices=[4, 5, 8]),
    ):

        await inter.response.send_message(
            embed=FS.Embed(description=f"{FS.Emotes.LOADING} Création du tournoi..."), ephemeral=True
        )
        tournament = Tournament2v2Roll(inter.guild, taille, name=nom)
        await tournament.build()
        await inter.edit_original_message(
            embed=FS.Embed(description=f"Tournois [{tournament.name}]({tournament.admin_message.jump_url}) créé !")
        )

    @tournament.sub_command(name="multi", description="Créer un tournoi à plusieurs phases")
    async def multi(
        self, inter: ApplicationCommandInteraction, taille: int = commands.Param(description="Nombre de phases", gt=0)
    ):
        await inter.response.defer(ephemeral=True)
        cancel_embed: disnake.Embed = FS.Embed(
            description="Création du tournoi annulé.",
            footer_text="Tu peux rejeter ce message pour le faire disparaître.",
        )

        phases: List[List[TournamentData]] = []

        def embeds(phases: List[List[TournamentData]]) -> List[disnake.Embed]:
            return [
                FS.Embed(
                    title="🏆 __**TOURNOI CRÉATION**__ 🏆",
                    description="\n\n".join(
                        [
                            f"{FS.Emotes.BRACKET} __**Phases {i+1}**___\n**Format de la phase :** `{phase[0].type_str}`\n**Nombre de groupe : **`{len(phase)}`\n**Taille des groupes :** `{phase[0].size}`"
                            for i, phase in enumerate(phases)
                        ]
                    ),
                )
            ]

        for phase_idx in range(taille):
            phase = await phaseCreation(inter, phase_idx, embeds(phases))
            if phase:
                phases.append(phase.tournaments)
            else:
                await inter.edit_original_message(embed=cancel_embed, view=None)

        title = "Validation"
        confirm = await confirmation(
            target=inter, embeds=embeds(phases), title=title, description="Confirmer la configuration ?"
        )
        if confirm:
            await inter.edit_original_message(
                embed=FS.Embed(title=title, description=f"{FS.Emotes.LOADING} Création des phases en cours..."),
                view=None,
            )
            for phase in phases:
                for group in phase:
                    await group.build()
            await inter.edit_original_message(
                embed=FS.Embed(
                    title=title,
                    description="Phases créées !",
                    footer_text="Tu peux rejeter ce message pour le faire disparaitre.",
                )
            )

        else:
            await inter.edit_original_message(embed=cancel_embed, view=None)

    @tournament.sub_command(name="regles", description="Obtenir les règles d'un format")
    async def tournament_rules(
        self,
        inter: disnake.ApplicationCommandInteraction,
        format: str = commands.Param(
            description="Le format dont tu veux obtenir les règles", choices=[Tournament2v2Roll.TYPE]
        ),
    ):
        if format == Tournament2v2Roll.TYPE:
            await inter.response.send_message(embed=Tournament2v2Roll.generic_rules())
        else:
            await inter.response.send_message(embed=FS.warning(f"Aucun format correspondant à `{format}`"))


def setup(bot: InteractionBot):
    bot.add_cog(Tournament(bot))
