import os
import disnake 
from disnake import ApplicationCommandInteraction
from disnake.ext.commands import InteractionBot
from cogs.Tournament.classes import Tournament2v2Roll
import modules.FastSnake as FS
from .classes import *

        
        
class Tournament2v2RollView(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction, bot, role : disnake.Role, ordered : bool = False, annonce : str = None, name : str = "Tournament", banner : str = FS.Images.Tournament.ClashBanner, loaded_from_save : bool = False):
        super().__init__(timeout=None)
        self.bot : InteractionBot = bot
        self.inter : ApplicationCommandInteraction = inter
        self.banner : str = banner
        self.annonce : str = annonce
        self.admin : disnake.Member = self.inter.author
        self.round_selected : Round = None
        self.match_selected : Match = None
        self.team_selected : Team = None
        self.role : disnake.Role = role
        
        self.arret_state : bool = False

        
        if not loaded_from_save:
            self.name : str = name
            self.tournament : Tournament2v2Roll = Tournament2v2Roll(self.name,role.members,ordered)
            self.tournament.generate()
            self.make_options()
            
    @staticmethod
    async def load_from_save(inter : ApplicationCommandInteraction, file : disnake.File) -> disnake.ui.View:
        tournament : Tournament2v2Roll = await Tournament2v2Roll.load_from_save(inter, file)
        role = await inter.guild.create_role(name=f"Tournois {tournament.name}")
        for player in tournament.players:
            await player.add_roles(role, reason="tournament load")
        tournamentView : Tournament2v2RollView = Tournament2v2RollView(inter, inter.bot, role, loaded_from_save=True)
        tournamentView.tournament : Tournament2v2Roll = tournament
        tournamentView.name : str = tournament.name
        tournamentView.make_options()
        await tournamentView.makeChannels()
        return tournamentView
        
    def make_options(self):
        self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji=FS.Emotes.Num[j+1]) for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round)]
        self.match_selection.placeholder = f"Display the rounds first!"
        self.match_selection.disabled = True
        self.set_team_1_score.disabled = True
        self.set_team_1_score.placeholder = "Select a match first."
        self.set_team_2_score.disabled = True
        self.set_team_2_score.placeholder = "Select a match first."
        self.discard_button.disabled = True
        self.update_button.label = "Display rounds"
        self.start.disabled = True
        
        
    async def makeChannels(self):
        everyone = self.inter.guild.default_role
        self.category = await self.inter.guild.create_category(name=f"🏆 {self.name} 🏆")
        cat_perm_everyone = disnake.PermissionOverwrite()
        cat_perm_everyone.send_messages = False
        cat_perm_everyone.connect = False
        await self.category.set_permissions(everyone,overwrite=cat_perm_everyone)
        cat_perm = disnake.PermissionOverwrite()
        cat_perm.send_messages = False
        cat_perm.connect = True
        await self.category.set_permissions(self.role,overwrite=cat_perm)
        
        self.channel_overview = await self.category.create_text_channel(name="📋 Annonces")
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
        if self.tournament.nb_matches_per_round == 1:
            self.voices.append([])
            for j in range(2):
                self.voices[0].append(await self.category.create_voice_channel(name=f"Team {j+1}"))
        else:      
            for i in range(self.tournament.nb_matches_per_round):
                self.voices.append([])
                for j in range(2):
                    self.voices[i].append(await self.category.create_voice_channel(name=f"Match {chr(ord('A') + i)} Team {j+1}"))
        
        self.message_rank = await self.channel_rank.send(embed=self.rank)
        self.message_rounds = await self.channel_rounds.send(embed=FS.Embed(
            title="📅 Rounds",
            description="*Les rounds seront affichés ici une fois que le tournoi aura commencé*",
            color = disnake.Colour.gold()
        ))
        self.message_rules = await self.channel_rules.send(embed=self.rules)
        self.message_overview = await self.channel_overview.send(
            content=self.role.mention,
            embed=FS.Embed(
                title=f"🏆 __**{self.name.upper()}**__ 🏆",
                description=(self.annonce if self.annonce else "Bienvenu dans ce tournoi !") + f"\n➖➖\n> [{self.channel_rank.mention}]({self.message_rank.jump_url}) pour voir le **classement en direct**.\n> [{self.channel_rounds.mention}]({self.message_rounds.jump_url}) pour **l'avancement des rounds.**\n> [{self.channel_rules.mention}]({self.message_rules.jump_url}) pour voir les **règles du tournoi.**\n> ➖➖\n> {self.voice_general.mention} pour rejoindre le **vocal du tournoi**",
                image=self.banner,
                color=disnake.Colour.blue()
            )
        )
        self.message_dashboard = await self.channel_dashboard.send(embeds=self.dashboard_embeds,view=self)
        
    def is_admin(self, inter : disnake.MessageInteraction):
        return inter.author.id == self.admin.id
    
        

    @property   
    def dashboard_embeds(self) -> List[disnake.Embed]: 
        embeds = []       
        embeds.append(self.tournament.detailedClassement)
        embeds += self.tournament.rounds_embeds(detailled= True)
        return embeds
    
    @property
    def rules(self) -> disnake.Embed:
        return self.tournament.rules
    
    @property
    def rank(self) -> disnake.Embed:
        return self.tournament.displayedClassement
    
    @property
    def rounds(self) -> List[disnake.Embed]:
        return self.tournament.rounds_embeds()
            
    async def update_dashboard(self, interaction : disnake.MessageInteraction, original = False):
        if (self.match_selected and self.round_selected) is not None:
            self.match_selection.placeholder = f"Round {self.round_selected.round_idx+1} Match {chr(ord('A') + self.match_selected.match_idx)}"
            self.set_team_1_score.disabled = False
            self.set_team_1_score.placeholder = f"{self.match_selected.teams[0].display_name} : {self.match_selected.teams[0].scores_description}"
            self.set_team_2_score.disabled = False
            self.set_team_2_score.placeholder = f"{self.match_selected.teams[1].display_name} : {self.match_selected.teams[1].scores_description}"
        else:
            self.match_selection.placeholder = f"Select a match"
            self.match_selection.options = [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="🆕") for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round) if not self.tournament.rounds[j].matches[i].is_played]
            self.match_selection.options += [disnake.SelectOption(label=f"Round {j+1} Match {chr(ord('A') + i)}",value=f"{j}{i}",emoji="↩️") for j in range(self.tournament.nb_rounds) for i in range(self.tournament.nb_matches_per_round) if self.tournament.rounds[j].matches[i].is_played]
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = f"Select a match first."
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = f"Select a match first."
        if self.tournament.current_round == None:
            self.start.disabled = True
        if original:
            await interaction.edit_original_message(
                embeds = self.dashboard_embeds,
                view = self
            )
        else:
            await interaction.response.edit_message(
                embeds = self.dashboard_embeds,
                view = self
            ) 
        
    async def update_infos(self):
        self.tournament.save_state()
        self.discard_button.disabled = True
        self.match_selection.disabled = False
        self.update_button.disabled = True
        self.start.disabled = False
        await self.message_rank.edit(embed=self.rank)
        await self.message_rounds.edit(embeds=self.rounds)
                     
    @disnake.ui.button(emoji = "✅", label = "Validate changes", style=disnake.ButtonStyle.green, row = 1)
    async def update_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            await self.update_infos()
            self.update_button.label = "Validate change"
            self.round_selected = None
            self.match_selected = None
            self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔁", label = "Discard changes", style=disnake.ButtonStyle.primary, row = 1)
    async def discard_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            self.tournament.restore_from_last_state()
            await self.update_infos()
            self.round_selected = None
            self.match_selected = None
            self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "🔊", label = "Move to channel", style=disnake.ButtonStyle.gray, row = 1)
    async def start(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            current_round = self.tournament.current_round
            if current_round != None:
                for i in range(self.tournament.nb_matches_per_round):
                    for j in range(2):
                        await current_round.matches[i].teams[j].move_to(self.voices[i][j])
            self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "⚠️", label = "End", style=disnake.ButtonStyle.danger, row = 1)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            if (await FS.confirmation(interaction,
                                   title=f"__**Tournament ending confirmation**__",
                                   message=f"⚠️ Are you sure that you want to end the tournament **{self.tournament.name}**? ⚠️",
                                   confirmationLabel="End the tournament",
                                   cancelLabel="Cancel",
                                   color=disnake.Colour.red())):
                self.stop()
                await interaction.edit_original_message(embed=FS.Embed(title=f"__**Tournament {self.tournament.name} ending**__", description="Ending... ⌛"), view=None)
                try:
                    file = disnake.File(self.tournament.state_file)
                    await self.admin.send(content=f'**__Tournois *"{self.tournament.name}"*__**',embeds=self.dashboard_embeds, file=file)
                    if os.path.exists(self.tournament.state_file):
                        os.remove(self.tournament.state_file)
                except OSError:
                    await self.admin.send(embeds=self.dashboard_embeds)
                    await self.admin.send(embed = FS.Embed(title=":x: ERROR :x:", description="Not able to load the files to discord.\nYou can acces them on the host machine and you should to delete them manually once you don't need them anymore."))
                for channel in self.category.channels:
                    await channel.delete()
                await self.category.delete()
                await self.role.delete()
                self.bot.tournaments_name.remove(self.name)
                if len(self.bot.tournaments_name) > 0:
                    await self.bot.change_presence(activity = disnake.Activity(name=", ".join(self.bot.tournaments_name), type=disnake.ActivityType.playing)) 
                else:
                    await self.bot.change_presence(activity=disnake.Game(name='"/" -> commandes'))
            else:
                await self.update_dashboard(interaction, original=True)            
        else:
            await self.update_dashboard(interaction)      
 
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2)
    async def match_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            self.round_selected = self.tournament.rounds[int(select.values[0][0])]
            self.match_selected = self.round_selected.matches[int(select.values[0][1])]
            self.arret_state = False
        await self.update_dashboard(interaction)
        
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 3,
                            options= [
                                disnake.SelectOption(label = "2 kills", emoji = "✅", value = "200"),
                                disnake.SelectOption(label = "1 kill & 1 turret", emoji = "✅", value = "110"),
                                disnake.SelectOption(label = "1 kill & 100 cs", emoji = "✅", value = "101"),
                                disnake.SelectOption(label = "1 kills", emoji = "❌", value = "100"),
                                disnake.SelectOption(label = "1 turret", emoji = "❌", value = "010"),
                                disnake.SelectOption(label = "100 cs", emoji = "❌", value = "001"),
                                disnake.SelectOption(label = "nothing", emoji = "❌", value = "000")
                            ])
    async def set_team_1_score(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            scores = [int(s) for s in select.values[0]]
            self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[0], scores)
            self.update_button.disabled = False
            self.match_selection.disabled = True
            self.discard_button.disabled = False
            self.start.disabled = True
            self.arret_state = False
        await self.update_dashboard(interaction)
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 4,
                            options= [
                                disnake.SelectOption(label = "2 kills", emoji = "✅", value = "200"),
                                disnake.SelectOption(label = "1 kill & 1 turret", emoji = "✅", value = "110"),
                                disnake.SelectOption(label = "1 kill & 100 cs", emoji = "✅", value = "101"),
                                disnake.SelectOption(label = "1 kills", emoji = "❌", value = "100"),
                                disnake.SelectOption(label = "1 turret", emoji = "❌", value = "010"),
                                disnake.SelectOption(label = "100 cs", emoji = "❌", value = "001"),
                                disnake.SelectOption(label = "nothing", emoji = "❌", value = "000")
                            ])
    async def set_team_2_score(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            scores = [int(s) for s in select.values[0]]
            self.tournament.set_scores(self.round_selected, self.match_selected, self.match_selected.teams[1], scores)
            self.update_button.disabled = False
            self.match_selection.disabled = True
            self.discard_button.disabled = False
            self.start.disabled = True
            self.arret_state = False
        await self.update_dashboard(interaction)
  
