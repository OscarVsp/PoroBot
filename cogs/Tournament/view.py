from typing import List
import disnake 
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from cogs.Tournament.modal import NotificationModal
import modules.FastSnake as FS
from modules.FastSnake.ChoicesView import ButtonChoice
from modules.FastSnake.Views import QCM, QRM, memberSelection
from .classes import Round,Match, State,Team, TournamentData

 
class TournamentView(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction, bot : InteractionBot, tournament : TournamentData):
        super().__init__(timeout=None)
        self.tournament : TournamentData = tournament
        self.round_selected : Round = None
        self.match_selected : Match = None
        self.team_selected : Team = None    
        self.make_options()   
        
    def make_options(self):
        self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji=FS.Emotes.Num(j+1)) for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round)]
        if len(self.match_selection.options) > 25:
            self.match_selection.options = self.match_selection.options[:25]
        self.set_team_1_score.options = self.make_score_options()
        self.set_team_1_score.max_values = self.tournament.nb_point_to_win_match
        self.set_team_1_score.disabled = True
        self.set_team_2_score.options = self.make_score_options()
        self.set_team_2_score.max_values = self.tournament.nb_point_to_win_match
        self.set_team_2_score.disabled = True
        self.discard_button.disabled = True
        
    def make_score_options(self):
        options = []
        blank_value : str = "0"*len(self.tournament.score_desriptor)
        for i,score in enumerate(self.tournament._scores_descriptor):
            for n in range(self.tournament.nb_point_to_win_match):
                value = blank_value
                value[i] = str(n+1)
                options.append(disnake.SelectOption(label=f"{n+1} {score}(s)",value=value,emoji=self.tournament.score_emoji[i]))
        options.append(disnake.SelectOption(label="Rien",value=blank_value,emoji="⭕"))
        return options
            
    
               
    async def update(self):
        if (self.match_selected and self.round_selected) is not None:
            self.match_selection.placeholder = f"Round {self.round_selected.round_idx+1} Match {chr(ord('A') + self.match_selected.match_idx)}"
            self.set_team_1_score.disabled = False
            self.set_team_1_score.placeholder = f"{self.match_selected.teams[0].display_name} : {self.match_selected.teams[0].scores_description}"
            self.set_team_2_score.disabled = False
            self.set_team_2_score.placeholder = f"{self.match_selected.teams[1].display_name} : {self.match_selected.teams[1].scores_description}"
        else:
            self.match_selection.placeholder = f"Select a match"
            self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="🆕") for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round) if not self.tournament.rounds[j].matches[i].state >= State.ENDED]
            self.match_selection.options += [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="↩️") for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round) if self.tournament.rounds[j].matches[i].state >= State.ENDED]
            if len(self.match_selection.options) > 25:
                self.match_selection.options = self.match_selection.options[:25]
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = f"Select a match first."
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = f"Select a match first."
        self.tournament.admin_message = await self.tournament.admin_message.edit(embeds=self.tournament.admin_embeds, view=self)
                     
    @disnake.ui.button(emoji = "✅", label = "Validate", style=disnake.ButtonStyle.green, row = 1)
    async def update_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.update_button.disabled = True
        self.discard_button.disabled = True
        self.match_selection.disabled = False
        self.start.disabled = False
        self.round_selected = None
        self.match_selected = None
        self.arret_state = False
        await self.tournament.update()
        await self.update()
        
    @disnake.ui.button(emoji = "🔁", label = "Cancel", style=disnake.ButtonStyle.primary, row = 1)
    async def discard_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.tournament.restore_from_last_state()
        self.round_selected = None
        self.match_selected = None
        self.arret_state = False
        await self.update()
        
    @disnake.ui.button(emoji = "🔔", label = "Annonce", style=disnake.ButtonStyle.gray, row = 1)
    async def notif(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.send_modal(NotificationModal(self))       
        
    @disnake.ui.button(emoji = "⚠️", label = "End", style=disnake.ButtonStyle.danger, row = 1)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        send_result = ButtonChoice(label="Send Result",emoji="📊")
        delete_role = ButtonChoice(label="Delete Role",emoji="👥")
        delete_category = ButtonChoice(label="Delete Category",emoji="🧹")
        choices = []
        choices += [send_result,delete_role,delete_category]
        pre_selection = choices.copy()
        confirmationQRM = await FS.QRM(
            interaction,
            choices,
            pre_selection,
            title=f"⚠️ __**Tournament ending confirmation**__ ",
            message=f"What do you want me to do while ending the phase ?",
            color=disnake.Colour.red()
        )
        if confirmationQRM:
            self.stop()
            self.tournament.end()
        else:
            await self.update()  

 
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="Select a match")
    async def match_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        self.round_selected = self.tournament.rounds[int(select.values[0][0])]
        self.match_selected = self.round_selected.matches[int(select.values[0][1])]
        self.arret_state = False
        await self.update()
                      
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="Select a first match",
                            options= [
                                disnake.SelectOption(label="placeholder")
                            ])
    async def set_team_1_score(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        scores = [int(s) for s in select.values[0]]
        self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[0], scores)
        self.update_button.disabled = False
        self.match_selection.disabled = True
        self.discard_button.disabled = False
        self.arret_state = False
        await self.update()
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 4, placeholder="Select a first match",
                            options= [
                                disnake.SelectOption(label="placeholder")
                            ])
    async def set_team_2_score(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        scores = [int(s) for s in select.values[0]]
        self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[1], scores)
        self.update_button.disabled = False
        self.match_selection.disabled = True
        self.discard_button.disabled = False
        self.arret_state = False
        await self.update()
  



