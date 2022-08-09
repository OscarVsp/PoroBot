import asyncio
from email import message
import disnake 
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from cogs.Tournament.modal import NotificationModal
import modules.FastSnake as FS
from modules.FastSnake.ChoicesView import ButtonChoice
from modules.FastSnake.Views import QCM, QRM, memberSelection
from .classes import *

#TODO check self.inter and self.bot uses ?

class TournamentView(disnake.ui.View):
    
    def __init__(self, inter : ApplicationCommandInteraction, bot : InteractionBot, role : disnake.Role, name : str = "Tournoi", description : str = None, banner : str = FS.Assets.Images.Tournament.ClashBanner):
        super().__init__(timeout=None)
        self.inter : ApplicationCommandInteraction = inter
        self.bot : InteractionBot = bot
        self.role : disnake.Role = role
        self.name : str = name
        self.desription : str = description
        self.banner : str = banner
        self.tournament : Tournament = Tournament(name,role)
        self.set_phase_players.disabled = True
        self.start_phase.disabled = True
        self.remove_phase.disabled = True
        
        
    
    async def update(self, inter : ApplicationCommandInteraction = None):
        self.start_phase.disabled = not self.tournament.next_phase_ready()
        self.set_phase_players.disabled = (len(self.tournament.phases) == 0)
        self.remove_phase.disabled = (len(self.tournament.phases) == 0)
        await asyncio.sleep(1)
        if inter == None:
            await self.inter.edit_original_message(
                embed = self.tournament.embed,
                view = self
            )
        else:
            if inter.response.is_done():
                await inter.edit_original_message(
                    embed = self.tournament.embed,
                    view = self
            )
            else:
                await inter.response.edit_message(
                    embed=self.tournament.embed,
                    view = self
                )
            
    @disnake.ui.button(label="Ajouter une phase",emoji="🆕", row = 1)
    async def add_phase(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        title = "Création d'une phase"
        message_header = ""
        positions = [FS.ButtonChoice(f"stage {i+1}",FS.Assets.Emotes.Num(i+1)) for i in range(len(self.tournament.phases)+1)]
        await asyncio.sleep(1)
        choice_pos = await QCM(interaction, positions, positions[len(positions)-1], title=title, message=message_header+"Position de la phase ?")
        if choice_pos:
            stage_idx = positions.index(choice_pos.response)
            message_header += f"> **Stage** {FS.Assets.Emotes.Num(stage_idx+1)}\n"
            types = [FS.ButtonChoice("Tournament Roll 2v2")]
            await asyncio.sleep(1)
            choice_type = await QCM(interaction,types,types[0],title=title,message=message_header+"Type de phase à créer ?")
            if choice_type:
                if choice_type.response == types[0]:
                    sizes = []
                    if len(self.role.members) >= 4:
                        sizes.append(FS.ButtonChoice("4 Joueurs",FS.Assets.Emotes.Num(4)))
                    if len(self.role.members) >= 5:
                        sizes.append(FS.ButtonChoice("5 Joueurs",FS.Assets.Emotes.Num(5)))
                    if len(self.role.members) >= 8:
                        sizes.append(FS.ButtonChoice("8 Joueurs",FS.Assets.Emotes.Num(8)))
                    if sizes == []:
                        await interaction.edit_original_message(
                            embed=FS.Embed(title=title,description="Au moins 4 joueurs pour ce format"), #TODO generic
                            view=None
                        )
                        await asyncio.sleep(3)
                    else:
                        message_header += f"> **{choice_type.label}**\n"
                        await asyncio.sleep(1)
                        choice_size = await QCM(interaction,sizes,sizes[0],title=title,message=message_header+"Nombre de joueurs dans la phase ?")
                        if choice_size:
                            size : int = 4 if choice_size.response == sizes[0] else (5 if choice_size == sizes[1] else 8)
                            new_phase : Phase2v2Roll = Phase2v2Roll(stage_idx,len(self.tournament.stages[stage_idx]) if len(self.tournament.stages) > stage_idx else 0,size)
                            new_phase.view = PhaseView(interaction, self.bot, new_phase, self.role)
                            message_header += f"> **{size} joueurs**\n"
                            await asyncio.sleep(1)
                            await interaction.edit_original_message(
                                embeds=[self.tournament.embed,FS.Embed(title=title, description=message_header+"*Création de la phase en cours...*")],
                                view = None
                            )
                            self.tournament.add_phase(new_phase,stage_idx)
                            await new_phase.view.initialize()
                        
        await self.update(interaction)
        
    @disnake.ui.button(label="Retirer une phase",emoji="❌", row = 2)
    async def remove_phase(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        title = "Suppression d'une phase"
        
        phases_options = [FS.ButtonChoice(f"Phase {phase.title}",FS.Assets.Emotes.Num(phase.stage_idx+1)) for phase in self.tournament.phases]
        await asyncio.sleep(1)
        phases_choice = await QRM(interaction,phases_options,title=title,message="Sélectionner la/les phase(s) à supprimer")
        if phases_choice:
            await asyncio.sleep(1)
            await interaction.edit_original_message(
                embeds=[self.tournament.embed,FS.Embed(title=title,description=f"Suppression des {len(phases_choice.responses)} phase(s) en cour...")],
                view = None
            )
            for phase_response in phases_choice.responses:
                await self.tournament.remove_phase(self.tournament.phases[phases_options.index(phase_response)])
        await self.update(interaction)
        
        
    def member_check(self,**kwargs):
        return kwargs.get('member') in self.role.members
        
        
    @disnake.ui.button(label="Sélectionner les joueurs d'une phase",emoji="👥", row = 3)
    async def set_phase_players(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        title = "Sélection des joueurs d'une phase"
        phases_option = [FS.ButtonChoice(f"{FS.Assets.Emotes.Alpha[phase.phase_idx]} {phase.name}", FS.Assets.Emotes.Num(phase.stage_idx)) for phase in self.tournament.phases if phase.state <= State.SET]

        phases_choice = await QCM(interaction,phases_option,phases_option[0],title=title,message="Sélection la phase")
        if phases_choice:
            phase = self.tournament.phases[phases_option.index(phases_choice.response)]
            selection = await memberSelection(interaction,title=title,message=f"> __{phase.title_emote}__\n Sélectionne les joueurs de la phase",size=phase.size,pre_selection=self.role.members,check=self.member_check)
            if selection:
                new_role : disnake.Role = await interaction.guild.create_role(name=f"{self.name}:{phase.title}")
                for member in selection.members:
                    await member.add_roles(new_role)
                await phase.set_role(new_role)
        await self.update(interaction)
        
        
    @disnake.ui.button(label="Démarrer la prochaine phase",emoji="⏭️", row = 4)
    async def start_phase(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer(ephemeral=True)
        for phase in self.tournament.next_phases():
            await phase.start()
        await self.update(interaction)
        
        
        
    
        

        
        
class PhaseView(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction, bot, phase : Phase, tournament_role : disnake.Role):
        super().__init__(timeout=None)
        self.bot : InteractionBot = bot
        self.inter : ApplicationCommandInteraction = inter
        self.phase : Phase = phase
        self.tournament_role : disnake.Role = tournament_role
        self.admin : disnake.Member = self.inter.author
        self.round_selected : Round = None
        self.match_selected : Match = None
        self.team_selected : Team = None       
        
    async def initialize(self):
        everyone = self.inter.guild.default_role
        self.category = await self.inter.guild.create_category(name=f"PHASE {self.phase.title.upper()}")
        cat_perm_everyone = disnake.PermissionOverwrite()
        cat_perm_everyone.send_messages = False
        cat_perm_everyone.connect = False
        await self.category.set_permissions(everyone,overwrite=cat_perm_everyone)
        cat_perm = disnake.PermissionOverwrite()
        cat_perm.send_messages = False
        cat_perm.connect = True
        await self.category.set_permissions(self.tournament_role,overwrite=cat_perm)
        
        self.channel_overview = await self.category.create_text_channel(name="🔔 Annonces")
        self.channel_rank = await self.category.create_text_channel(name="🏅 Classement")
        self.channel_rounds = await self.category.create_text_channel(name="📅 Rounds")
        self.channel_rules = await self.category.create_text_channel(name="📜 Règles")
        
        self.channel_dashboard = await self.category.create_text_channel(name="🔧 Admin dashboard")
        dash_perm = disnake.PermissionOverwrite()
        dash_perm.view_channel = False
        await self.channel_dashboard.set_permissions(everyone,overwrite=dash_perm)
        admin_perm = disnake.PermissionOverwrite()
        admin_perm.view_channel = True
        await self.channel_dashboard.set_permissions(self.admin,overwrite=admin_perm)
        
        voice_perm = disnake.PermissionOverwrite()
        voice_perm.connect = True
        voice_perm.send_messages = True
        self.voice_general = await self.category.create_voice_channel(name="🏆 General")
        await self.voice_general.set_permissions(everyone,overwrite=voice_perm)
        self.voices : List[List[disnake.VoiceChannel]]= []
        if self.phase.nb_matches_per_round == 1:
            self.voices.append([])
            for j in range(2):
                self.voices[0].append(await self.category.create_voice_channel(name=f"Team {j+1}"))
        else:      
            for i in range(self.phase.nb_matches_per_round):
                self.voices.append([])
                for j in range(2):
                    self.voices[i].append(await self.category.create_voice_channel(name=f"Match {chr(ord('A') + i)} Team {j+1}"))
        
        self.message_rank : disnake.Message = await self.channel_rank.send(embed=self.phase.classement_embed)
        self.message_rounds : disnake.Message = await self.channel_rounds.send(embeds=self.phase.rounds_embeds)
        self.message_rules : disnake.Message = await self.channel_rules.send(embed=self.phase.rules_embed)
        self.message_dashboard : disnake.Message = await self.channel_dashboard.send(embeds=self.phase.admin_embeds)
        
    async def generate(self):
        self.make_options()
        await self.update_infos()
        await self.update_dashboard()
        
    def make_options(self):
        self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji=FS.Emotes.Num(j+1)) for j in range(self.phase.nb_rounds) for i in range(self.phase.nb_matches_per_round)]
        if len(self.match_selection.options) > 25:
            self.match_selection.options = self.match_selection.options[:25]
        self.set_team_1_score.options = self.make_score_options()
        self.set_team_1_score.max_values = self.phase.nb_point_to_win_match
        self.set_team_1_score.disabled = True
        self.set_team_2_score.options = self.make_score_options()
        self.set_team_2_score.max_values = self.phase.nb_point_to_win_match
        self.set_team_2_score.disabled = True
        self.discard_button.disabled = True
        self.start.disabled = True
        
    def make_score_options(self):
        options = []
        blank_value : str = "0"*len(self.phase.score_desriptor)
        for i,score in enumerate(self.phase._scores_descriptor):
            for n in range(self.phase.nb_point_to_win_match):
                value = blank_value
                value[i] = str(n+1)
                options.append(disnake.SelectOption(label=f"{n+1} {score}(s)",value=value,emoji=self.phase.score_emoji[i]))
        options.append(disnake.SelectOption(label="Rien",value=blank_value,emoji="⭕"))
        return options
            
    def annonce_embed(self, title : str, description : str) -> disnake.Embed:
        return FS.Embed(
                author_name=f"{self.phase.title.upper()}",
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
            self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="🆕") for j in range(self.phase.nb_rounds) for i in range(self.phase.nb_matches_per_round) if not self.phase.rounds[j].matches[i].state >= State.ENDED]
            self.match_selection.options += [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="↩️") for j in range(self.phase.nb_rounds) for i in range(self.phase.nb_matches_per_round) if self.phase.rounds[j].matches[i].state >= State.ENDED]
            if len(self.match_selection.options) > 25:
                self.match_selection.options = self.match_selection.options[:25]
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = f"Select a match first."
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = f"Select a match first."
        if self.phase.current_round == None:
            self.start.disabled = True
        if interaction:
            if interaction.response.is_done():
                await interaction.edit_original_message(
                    embeds=self.phase.admin_embeds,
                    view = self
                )
            else:
                await interaction.response.edit_message(
                    embeds = self.phase.admin_embeds,
                    view = self
                ) 
        else:
            await self.inter.edit_original_message(
                embeds = self.phase.admin_embeds,
                view = self
            )

    async def update_infos(self):
        self.phase.save_state()
        self.discard_button.disabled = True
        self.match_selection.disabled = False
        self.update_button.disabled = True
        self.start.disabled = False
        await self.message_rank.edit(embed=self.phase.classement_embed)
        await self.message_rounds.edit(embeds=self.phase.rounds_embeds)
        
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
        self.phase.restore_from_last_state()
        await self.update_infos()
        self.round_selected = None
        self.match_selected = None
        self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔊", label = "Vocal", style=disnake.ButtonStyle.gray, row = 1)
    async def start(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        current_round = self.phase.current_round
        if current_round != None:
            for i in range(self.phase.nb_matches_per_round):
                for j in range(self.phase.nb_teams_per_match):
                    for k in range(self.phase.nb_players_per_team):
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
            await interaction.edit_original_message(embed=FS.Embed(title=f"__**Tournament {self.phase.name} ending**__", description="Ending... ⌛"), view=None)
        
            if send_result in confirmationQRM.responses:
                await self.inter.author.send(content=f'**__Tournois *"{self.phase.name}"*__**',embeds=self.phase.admin_embeds)
            
            if delete_role in confirmationQRM.responses:
                await self.phase.role.delete()
            
            if delete_category in confirmationQRM.responses:
                await self.delete_cat()
        else:
            await self.update_dashboard(interaction, original=True)    

 
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2, placeholder="Select a match")
    async def match_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        self.round_selected = self.phase.rounds[int(select.values[0][0])]
        self.match_selected = self.round_selected.matches[int(select.values[0][1])]
        self.arret_state = False
        await self.update_dashboard(interaction)
                      
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3, placeholder="Select a first match",
                            options= [
                                disnake.SelectOption(label="placeholder")
                            ])
    async def set_team_1_score(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        scores = [int(s) for s in select.values[0]]
        self.phase.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[0], scores)
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
        self.phase.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[1], scores)
        self.update_button.disabled = False
        self.match_selection.disabled = True
        self.discard_button.disabled = False
        self.start.disabled = True
        self.arret_state = False
        await self.update_dashboard(interaction)
  



