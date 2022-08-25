from lib2to3.pgen2.token import TILDE
from typing import List
import disnake
from cogs.Tournament.modal import NotificationModal
import modules.FastSnake as FS
from modules.FastSnake import *
from .classes import Round, Match, State, Team, TournamentData


class PlayerSelectionView(MemberSelectionView):
    def __init__(self, tournament: TournamentData):
        super().__init__(
            target=tournament.admin_channel,
            embeds=[],
            title=tournament._admin_title,
            description="Sélectionne les participants.",
            timeout=None,
            size=tournament.size,
        )
        self.tournament: TournamentData = tournament

    async def end(self) -> None:
        await super().end()
        if self.state == ViewState.CONFIRMED:
            await self.tournament.set_players(self.selected_members)
        else:
            await self.tournament.delete()


class AdminView(disnake.ui.View):
    def __init__(self, tournament: TournamentData):
        super().__init__(timeout=None)
        self.tournament: TournamentData = tournament
        self.round_selected: Round = None
        self.match_selected: Match = None
        self.team_selected: Team = None
        self.blank_score: List[int] = [0 for _ in range(self.tournament._scoreSet.size)]

        self.set_team_1_score.options = self.tournament._scoreSet.options
        self.set_team_1_score.max_values = self.tournament.nb_point_to_win_match
        self.set_team_2_score.options = self.tournament._scoreSet.options
        self.set_team_2_score.max_values = self.tournament.nb_point_to_win_match
        self.discard_button.disabled = True
        self.update_button.disabled = True

        self.refresh_options()

    def refresh_options(self) -> None:
        if self.match_selected and self.round_selected:
            self.match_selection.placeholder = f"{self.round_selected.round_idx+1}{chr(ord('A') + self.match_selected.match_idx)} : {self.match_selected.teams[0].display_name} VS {self.match_selected.teams[1].display_name}"
            self.set_team_1_score.disabled = False
            self.set_team_1_score.placeholder = (
                f"{self.match_selected.teams[0].display_name} : {self.match_selected.teams[0].scores_description}"
            )
            self.set_team_2_score.disabled = False
            self.set_team_2_score.placeholder = (
                f"{self.match_selected.teams[1].display_name} : {self.match_selected.teams[1].scores_description}"
            )
        else:
            self.match_selection.placeholder = f"Sélectionner un match"
            self.match_selection.options = [
                disnake.SelectOption(
                    label=f"Round {j+1} - Match{chr(ord('A') + i)}",
                    description=f"{self.tournament.rounds[j].matches[i].teams[0].display_name} VS {self.tournament.rounds[j].matches[i].teams[1].display_name}",
                    value=f"{j}{i}",
                    emoji="🆕",
                )
                for j in range(self.tournament.nb_rounds)
                for i in range(self.tournament.nb_matches_per_round)
                if not self.tournament.rounds[j].matches[i].state >= State.ENDED
            ]
            self.match_selection.options += [
                disnake.SelectOption(
                    label=f"Round {j+1} - Match{chr(ord('A') + i)}",
                    description=f"{self.tournament.rounds[j].matches[i].teams[0].display_name} VS {self.tournament.rounds[j].matches[i].teams[1].display_name}",
                    value=f"{j}{i}",
                    emoji=FS.Emotes.RESTART,
                )
                for j in range(self.tournament.nb_rounds)
                for i in range(self.tournament.nb_matches_per_round)
                if self.tournament.rounds[j].matches[i].state >= State.ENDED
            ]
            if len(self.match_selection.options) > 25:
                self.match_selection.options = self.match_selection.options[:25]
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = f"Score de l'équipe 1"
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = f"Score de l'équipe 2"

    async def update(self, interaction: disnake.MessageInteraction) -> None:
        self.refresh_options()
        if interaction.response.is_done():
            await interaction.edit_original_message(embeds=self.tournament.admin_embeds, view=self)
        else:
            await interaction.response.edit_message(embeds=self.tournament.admin_embeds, view=self)

    def reset_selection(self) -> None:
        self.update_button.disabled = True
        self.discard_button.disabled = True
        self.match_selection.disabled = False
        self.round_selected = None
        self.match_selected = None

    @disnake.ui.button(emoji="✅", label="Valider", style=disnake.ButtonStyle.green, row=1)
    async def update_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.reset_selection()
        await self.tournament.update()
        await self.update(interaction)

    @disnake.ui.button(emoji=FS.Emotes.RESTART, label="Annuler", style=disnake.ButtonStyle.primary, row=1)
    async def discard_button(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.reset_selection()
        self.tournament.restore_from_last_state()
        await self.tournament.update()
        await self.update(interaction)

    @disnake.ui.button(emoji="🔔", label="Annonce", style=disnake.ButtonStyle.gray, row=1)
    async def notif(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(NotificationModal(self.tournament))

    @disnake.ui.button(emoji="⚠️", label="Stop", style=disnake.ButtonStyle.danger, row=1)
    async def arret(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        confirmation = await FS.confirmation(
            interaction,
            embeds=self.tournament.admin_embeds,
            title=f"⚠️ __**ARRÊTER LE TOURNOI**__ ",
            description=f"Es-tu sûr de vouloir arrêter le tournoi ?\nCela va supprimer tout les channels de la catégorie et t'envoyer les résultats en privé.",
            color=disnake.Colour.red(),
        )
        if confirmation:
            self.stop()
            await interaction.edit_original_message(
                embed=FS.Embed(
                    title=self.tournament._admin_title, description=f"{FS.Emotes.LOADING} Suppression du tournoi..."
                ),
                view=None,
            )
            await self.tournament.delete(interaction)
        else:
            await self.update(interaction)

    @disnake.ui.select(min_values=1, max_values=1, row=2, placeholder="Sélectionner un match")
    async def match_selection(self, select: disnake.ui.Select, interaction: disnake.MessageInteraction):
        self.round_selected = self.tournament.rounds[int(select.values[0][0])]
        self.match_selected = self.round_selected.matches[int(select.values[0][1])]
        await self.update(interaction)

    @disnake.ui.select(
        min_values=1,
        max_values=1,
        row=3,
        placeholder="Score de l'équipe 1",
        options=[disnake.SelectOption(label="placeholder")],
    )
    async def set_team_1_score(self, select: disnake.ui.Select, interaction: disnake.MessageInteraction):
        scores = self.blank_score.copy()
        for score in select.values:
            if score != "-":
                scores[int(score[0])] += 1
        self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[0], scores)
        self.update_button.disabled = False
        self.discard_button.disabled = False
        await self.update(interaction)

    @disnake.ui.select(
        min_values=1,
        max_values=1,
        row=4,
        placeholder="Score de l'équipe 1",
        options=[disnake.SelectOption(label="placeholder")],
    )
    async def set_team_2_score(self, select: disnake.ui.Select, interaction: disnake.MessageInteraction):
        scores = self.blank_score.copy()
        for score in select.values:
            if score != "-":
                scores[int(score[0])] += 1
        self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[1], scores)
        self.update_button.disabled = False
        self.discard_button.disabled = False
        await self.update(interaction)
