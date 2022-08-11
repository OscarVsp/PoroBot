from typing import List
import disnake 
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from cogs.Tournament.modal import NotificationModal
import modules.FastSnake as FS
from modules.FastSnake.ChoicesView import ButtonChoice
from modules.FastSnake.Views import QCM, QRM, memberSelection
from .classes import Round,Match,Team, TournamentData

#TODO check self.inter and self.bot uses ?


class InitView(disnake.ui.view):
    
    def __init__(self) -> None:
        super().__init__(timeout=None)
        
    @disnake.ui.button(label="Select players")
    async def select_players(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        await memberSelection(interaction,title="Sélectionne les joueurs")
        
        
        
        
        
        
       
  
class TournamentView(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction, bot : InteractionBot, tournament : TournamentData):
        super().__init__(timeout=None)
        self.bot : InteractionBot = bot
        self.inter : ApplicationCommandInteraction = inter
        self.tournament : TournamentData = tournament
        self.round_selected : Round = None
        self.match_selected : Match = None
        self.team_selected : Team = None       
        
    async def initialize(self):
        everyone = self.inter.guild.default_role
        self.category = await self.inter.guild.create_category(name=f"TOURNAMENT {self.tournament.name.upper()}")
        cat_perm_everyone = disnake.PermissionOverwrite()
        cat_perm_everyone.send_messages = False
        cat_perm_everyone.connect = True
        await self.category.set_permissions(everyone,overwrite=cat_perm_everyone)
        
        self.channel_overview = await self.category.create_text_channel(name="🔔 Annonces")
        self.channel_rank = await self.category.create_text_channel(name="🏅 Classement")
        self.channel_rounds = await self.category.create_text_channel(name="📅 Rounds")
        self.channel_rules = await self.category.create_text_channel(name="📜 Règles")
        
        self.channel_dashboard = await self.category.create_text_channel(name="🔧 Admin dashboard")
        dash_perm = disnake.PermissionOverwrite()
        dash_perm.view_channel = False
        await self.channel_dashboard.set_permissions(everyone,overwrite=dash_perm)
        
        voice_perm = disnake.PermissionOverwrite()
        voice_perm.connect = True
        voice_perm.send_messages = True
        self.voice_general = await self.category.create_voice_channel(name="🏆 General")
        await self.voice_general.set_permissions(everyone,overwrite=voice_perm)
        self.voices : List[List[disnake.VoiceChannel]]= []
        if self.tournament.nb_matches_per_round == 1:
            self.voices.append([])
            for j in range(2):
                self.voices[0].append(await self.category.create_voice_channel(name=f"Team {j+1}"))
        else:      
            for i in range(self.tournament.nb_matches_per_round):
                self.voices.append([])
                for j in range(2):
                    self.voices[i].append(await self.category.create_voice_channel(name=f"Match {chr(ord('A') + i)} Team {j+1}"))
        
        self.message_rank : disnake.Message = await self.channel_rank.send(embed=self.tournament.classement_embed)
        self.message_rounds : disnake.Message = await self.channel_rounds.send(embeds=self.tournament.rounds_embeds)
        self.message_rules : disnake.Message = await self.channel_rules.send(embed=self.tournament.rules_embed)
        player_selection_button = disnake.ui.Button(label = "Sélectionner les joueurs")
        player_selection_button.callback = self.player_selection_callback
        self.message_dashboard : disnake.Message = await self.channel_dashboard.send(embeds=self.tournament.admin_embeds, components=[player_selection_button])
        
    async def player_selection_callback(self, inter : disnake.MessageInteraction):
        await inter.response.defer()
        selection = await memberSelection(inter, title=f"Sélection des joueurs",message=f"Sélectionne les participants du tournoi.",size=self.tournament.size)
        if selection:
            self.tournament.set_players(selection.members)
            pass
        
    async def generate(self):
        self.make_options()
        await self.update_infos()
        await self.update_dashboard()
        
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
        self.start.disabled = True
        
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
            
    def annonce_embed(self, title : str, description : str) -> disnake.Embed:
        return FS.Embed(
                author_name=f"{self.tournament.title.upper()}",
                author_icon_url=FS.Assets.Images.Tournament.Trophy,
                title = title,
                description=description,
                color=disnake.Colour.blue()
            )
               
    async def update_dashboard(self, interaction : disnake.MessageInteraction = None):
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
        if self.tournament.current_round == None:
            self.start.disabled = True
        if interaction:
            if interaction.response.is_done():
                await interaction.edit_original_message(
                    embeds=self.tournament.admin_embeds,
                    view = self
                )
            else:
                await interaction.response.edit_message(
                    embeds = self.tournament.admin_embeds,
                    view = self
                ) 
        else:
            await self.inter.edit_original_message(
                embeds = self.tournament.admin_embeds,
                view = self
            )

    async def update_infos(self):
        self.tournament.save_state()
        self.discard_button.disabled = True
        self.match_selection.disabled = False
        self.update_button.disabled = True
        self.start.disabled = False
        await self.message_rank.edit(embed=self.tournament.classement_embed)
        await self.message_rounds.edit(embeds=self.tournament.rounds_embeds)
        
    async def update(self, inter : ApplicationCommandInteraction = None):
        await self.update_dashboard(inter)
        await self.update_infos()
                     
    @disnake.ui.button(emoji = "✅", label = "Validate", style=disnake.ButtonStyle.green, row = 1)
    async def update_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        await self.update_infos()
        self.update_button.label = "Validate"
        self.round_selected = None
        self.match_selected = None
        self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔁", label = "Cancel", style=disnake.ButtonStyle.primary, row = 1)
    async def discard_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.tournament.restore_from_last_state()
        await self.update_infos()
        self.round_selected = None
        self.match_selected = None
        self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔊", label = "Vocal", style=disnake.ButtonStyle.gray, row = 1)
    async def start(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        current_round = self.tournament.current_round
        if current_round != None:
            for i in range(self.tournament.nb_matches_per_round):
                for j in range(self.tournament.nb_teams_per_match):
                    for k in range(self.tournament.nb_players_per_team):
                        player = current_round.matches[i].teams[j].players[k]
                        if player.voice.channel == self.voice_general:
                            await player.move_to(self.voices[i][j])
        self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔔", label = "Annonce", style=disnake.ButtonStyle.gray, row = 1)
    async def notif(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.send_modal(NotificationModal(self))
        
    async def delete_cat(self):
        for channel in self.category.channels:
            await channel.delete()
        await self.category.delete()     
       
        
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
            await interaction.edit_original_message(embed=FS.Embed(title=f"__**Tournament {self.tournament.name} ending**__", description="Ending... ⌛"), view=None)
        
            if send_result in confirmationQRM.responses:
                await self.inter.author.send(content=f'**__Tournois *"{self.tournament.name}"*__**',embeds=self.tournament.admin_embeds)
            
            if delete_role in confirmationQRM.responses:
                await self.tournament.role.delete()
            
            if delete_category in confirmationQRM.responses:
                await self.delete_cat()
        else:
            await self.update_dashboard(interaction, original=True)    

 
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="Select a match")
    async def match_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        self.round_selected = self.tournament.rounds[int(select.values[0][0])]
        self.match_selected = self.round_selected.matches[int(select.values[0][1])]
        self.arret_state = False
        await self.update_dashboard(interaction)
                      
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
        self.start.disabled = True
        self.arret_state = False
        await self.update_dashboard(interaction)
        
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
        self.start.disabled = True
        self.arret_state = False
        await self.update_dashboard(interaction)
  



