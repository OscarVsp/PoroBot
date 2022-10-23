# -*- coding: utf-8 -*-
from typing import List

import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands
from disnake.ext.commands import InteractionBot

import modules.FastSnake as FS
from .classes import State
from .classes import TournamentData
from .TournamentManager import Tournament as TournamentClass
from .TournamentManager import Tournament2v2Roll
from .TournamentMutliView import phaseCreation
from bot.bot import Bot
from cogs.Tournament.TournamentView import PlayerSelectionView
from modules.FastSnake import confirmation


class Tournament(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot
        self.tournaments: List[TournamentClass] = []

    @commands.slash_command(
        name="tournament", default_member_permissions=disnake.Permissions.all(), dm_permission=False
    )
    async def tournament(self, inter):
        pass

    @tournament.sub_command(name="new", description="Créer un tournoi")
    async def new_tournament(
        self,
        inter: ApplicationCommandInteraction,
        format: str = commands.Param(description="Le format à créer", choices=[Tournament2v2Roll.TYPE]),
        taille: str = commands.Param(description="Nombre de participants"),
        nom: str = commands.Param(description="Nom du tournoi"),
    ):

        await inter.response.defer(ephemeral=True)
        if format == Tournament2v2Roll.TYPE:
            if int(taille) not in Tournament2v2Roll.SIZES:
                await inter.edit_original_message(
                    embed=disnake.Embed(
                        description="Ce format nécessite "
                        + ", ".join([str(i) for i in Tournament2v2Roll.SIZES])
                        + " joueurs !"
                    )
                )
                return
            tournament = Tournament2v2Roll(inter.guild, int(taille), name=nom)
        else:
            await inter.edit_original_message(embed=disnake.Embed(description=f"Le format {format} n'éxiste pas..."))
            return
        self.tournaments.append(tournament)
        await tournament.build()
        await inter.edit_original_message(embed=FS.Embed(description=f"Tournois **{tournament.name}** créé !"))

    @new_tournament.autocomplete("taille")
    async def new_tournament_taille(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        if inter.filled_options.get("format") == Tournament2v2Roll.TYPE:
            return [str(i) for i in Tournament2v2Roll.SIZES]
        else:
            return ["2", "4", "5", "6", "8", "10", "12", "14", "16", "20"]

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

    @tournament.sub_command(name="start", description="Sélectionner les joueurs et démarrer le tournois")
    async def start_tournament(
        self, inter: ApplicationCommandInteraction, tournament: str = commands.Param(description="Le tournoi à start"), shuffle: bool = commands.Param(description="Mélanger les joueurs avant de faire les rounds", default=False)
    ):
        await inter.response.defer(ephemeral=True)
        _tournament = next(
            (_tournament for _tournament in self.tournaments if _tournament.name.lower() == tournament.lower())
        )
        if _tournament:
            await PlayerSelectionView(_tournament, inter, shuffle).send()

    @start_tournament.autocomplete("tournament")
    async def start_autocomplete(self, inter: ApplicationCommandInteraction, user_input: str):
        return [
            tournament.name for tournament in self.tournaments if tournament.name.lower().startswith(user_input.lower())
        ]

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

    @commands.Cog.listener("on_message")
    async def on_message(self, message: disnake.Message):
        if not message.author.bot:
            for tournament in self.tournaments:
                if tournament.state != State.ENDED:
                    await tournament.on_message(message)


def setup(bot: InteractionBot):
    bot.add_cog(Tournament(bot))
