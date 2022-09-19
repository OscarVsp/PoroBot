# -*- coding: utf-8 -*-
from typing import List

import disnake

import modules.FastSnake as FS
from .TournamentManager import *
from modules.FastSnake import *


class PhaseCreationView(ConfirmationView):
    def __init__(self, target: Target, embeds: List[disnake.Embed], phase_idx: int):
        super().__init__(
            target,
            embeds,
            f"{FS.Emotes.BRACKET} __**CRÉATION DE LA PHASE {phase_idx+1}**__",
            "Configure la phase avec les options ci-dessous.",
            300,
        )
        self.phase_idx: int = phase_idx
        self.size.disabled = True
        self.confirm.disabled = True
        self.format_text: str = None
        self.nombre_group: int = None
        self.taille_groups: int = None
        self.tournaments: List[Tournament] = []

    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        embed.description += "\n**Format de la phase :** " + (f"`{self.format_text}`" if self.format_text else "`N/A`")
        embed.description += "\n**Nombre de groupe :** " + (f"`{self.nombre_group}`" if self.nombre_group else "`N/A`")
        embed.description += "\n**Taille des groupes :** " + (
            f"`{self.taille_groups}`" if self.taille_groups else "`N/A`"
        )
        return embed

    async def update(self, inter: disnake.MessageInteraction):
        if self.format_text:
            if self.format_text == Tournament2v2Roll.TYPE and self.size.disabled:
                self.size.placeholder = "Taille des groupe"
                self.size.options = [
                    disnake.SelectOption(
                        label=" joueurs",
                        value=str(i),
                        emoji=FS.Emotes.Num(i),
                        description=f"Pour un total de {i-1} rounds",
                    )
                    for i in [4, 5, 8]
                ]
                self.size.disabled = False
        return await super().update(inter)

    @disnake.ui.select(
        placeholder="Format de la phase",
        options=[
            disnake.SelectOption(
                label=Tournament2v2Roll.TYPE,
                emoji="🔀",
                description="Robin round par équipes de deux qui changent entre chaque round.",
            )
        ],
    )
    async def phase(self, select: disnake.ui.Select, inter: disnake.MessageInteraction):
        self.format_text = select.values[0]
        select.placeholder = select.values[0]
        await self.update(inter)

    @disnake.ui.select(
        placeholder="Nombre de groupe",
        options=[
            disnake.SelectOption(
                label=f"{i+1}",
                value=str(i + 1),
                description=f"{i+1} groupe" + ("s" if i > 0 else "") + " en parrallèle",
            )
            for i in range(25)
        ],
    )
    async def group(self, select: disnake.ui.Select, inter: disnake.MessageInteraction):
        self.nombre_group = int(select.values[0])
        select.placeholder = select.values[0]
        await self.update(inter)

    @disnake.ui.select(
        placeholder="Taille des groupe (sélectionne d'abord le format)",
        options=[disnake.SelectOption(label="Placeholder")],
    )
    async def size(self, select: disnake.ui.Select, inter: disnake.MessageInteraction):
        self.taille_groups = int(select.values[0])
        select.placeholder = select.values[0]
        self.confirm.disabled = False
        await self.update(inter)


class PhaseCreationReturnData(ConfirmationReturnData):
    def __init__(self, phaseCreationView: PhaseCreationView):
        super().__init__(phaseCreationView)
        self.tournaments: List[Tournament] = []
        if self.is_ended:
            for i in range(phaseCreationView.nombre_group):
                if phaseCreationView.format_text == Tournament2v2Roll.TYPE:
                    self.tournaments.append(
                        Tournament2v2Roll(
                            phaseCreationView.target.guild,
                            phaseCreationView.taille_groups,
                            f"PHASE {phaseCreationView.phase_idx+1}"
                            + (f" - GROUPE {chr(ord('A') +i)}" if phaseCreationView.nombre_group > 1 else ""),
                        )
                    )


async def phaseCreation(
    inter: disnake.ApplicationCommandInteraction, phase_idx: int, embeds: List[disnake.Embed]
) -> PhaseCreationReturnData:
    phaseCreationView = PhaseCreationView(inter, embeds, phase_idx)
    await phaseCreationView.send()
    await phaseCreationView.wait()
    return PhaseCreationReturnData(phaseCreationView)
