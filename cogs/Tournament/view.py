import disnake 
from disnake import ApplicationCommandInteraction
from cogs.Tournament.classes import Tournament2v2Roll
from utils.FastEmbed import FastEmbed
from random import choices
from utils.data import emotes,color
from .classes import *
import asyncio
import pickledb

tournamentdb = pickledb.load("cogs/Basic/tournament.db", False)
        
        
class Tournament2v2RollView(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction, bot, role : disnake.Role, name : str = "Tournament"):
        super().__init__(timeout=None)
        self.bot = bot
        self.inter = inter
        self.name = name
        self.role = role
        self.players = [Player(p) for p in role.members]
        self.tournament = Tournament2v2Roll(self.players)
        self.tournament.generate()
        
        
        self.admin = self.inter.author
        self.match_selected = None
        self.team_selected = None
        self.max_round = 0
        
        self.make_options()
        
    def make_options(self):
        self.previous.disabled = True
        if self.tournament.nb_matchs_per_round == 1:
            self.match_selected = self.tournament.current_round.matches[0] 
            self.match_selection.disabled = True 
            self.match_selection.options = [disnake.SelectOption(
                    label=f"Only one match",
                    value="0"
                )]
            self.match_selection.placeholder = "Only one match per round." 
            self.set_team_1_score.disabled = False
            self.set_team_1_score.placeholder = f"{self.match_selected.teams[0].name} : {self.match_selected.teams[0].score}"
            self.set_team_2_score.disabled = False
            self.set_team_2_score.placeholder = f"{self.match_selected.teams[1].name} : {self.match_selected.teams[1].score}"      
        else:
            self.match_selection.options = [
                disnake.SelectOption(
                    label=f"{emotes.alpha[i]} Match {chr(ord('A') + i)}",
                    value=str(i)
                ) for i in range(self.tournament.nb_matchs_per_round)
            ]
            self.match_selection.placeholder = f"Select a match"
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = "Select a match first."
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = "Select a match first."
        
        
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
        self.voice_general = await self.category.create_voice_channel(name="🏆 General")
        await self.voice_general.set_permissions(everyone,overwrite=voice_perm)
        self.voices = []
        if self.tournament.nb_matchs_per_round == 1:
            self.voices.append([])
            for j in range(2):
                self.voices[0].append(await self.category.create_voice_channel(name=f"Team {j+1}"))
        else:      
            for i in range(self.tournament.nb_matchs_per_round):
                self.voices.append([])
                for j in range(2):
                    self.voices[i].append(await self.category.create_voice_channel(name=f"Match {chr(ord('A') + i)} Team {j+1}"))
        
        self.message_rank = await self.channel_rank.send(embed=self.rank)
        self.message_rounds = await self.channel_rounds.send(embed=FastEmbed(
            title="📅 Rounds",
            description="Les rounds seront affichés ici une fois que le tournoi aura commencé",
            color = color.Gold
        ))
        await self.channel_rules.send(embed=self.rules)
        self.message_dashboard = await self.channel_dashboard.send(embeds=self.embeds,view=self)
        
    def is_admin(self, inter):
        return inter.author.id == self.admin.id
        

    @property   
    def embeds(self): 
        embeds = []       
        embeds.append(self.tournament.detailedClassement)
        for i in range(self.tournament.rounds.index(self.tournament.current_round)+1):
            embeds.append(self.tournament.rounds[i].embed)
        return embeds
    
    @property
    def rules(self):
        return self.tournament.rules
    
    @property
    def rank(self):
        return self.tournament.classement
    
    @property
    def rounds(self):
        embeds = []       
        for i in range(self.max_round+1):
            embeds.append(self.tournament.rounds[i].embed)
        return embeds
            
    async def update_dashboard(self, interaction : disnake.MessageInteraction):
        if self.match_selected is not None:
            if self.tournament.nb_matchs_per_round > 1:
                self.match_selection.placeholder = f"{emotes.alpha[int(self.tournament.current_round.matches.index(self.match_selected))]} Match {chr(ord('A') + int(self.tournament.current_round.matches.index(self.match_selected)))}"
            self.set_team_1_score.disabled = False
            self.set_team_1_score.placeholder = f"{self.match_selected.teams[0].name} : {self.match_selected.teams[0].score}"
            self.set_team_2_score.disabled = False
            self.set_team_2_score.placeholder = f"{self.match_selected.teams[1].name} : {self.match_selected.teams[1].score}"
        else:
            self.match_selection.placeholder = f"Select a match"
            self.set_team_1_score.disabled = True
            self.set_team_1_score.placeholder = f"No match selected"
            self.set_team_2_score.disabled = True
            self.set_team_2_score.placeholder = f"No match selected"
        await interaction.response.edit_message(
                embeds = self.embeds,
                view = self
            ) 
        
    async def update_infos(self):
        if self.tournament.rounds.index(self.tournament.current_round) > self.max_round: 
                self.max_round = self.tournament.rounds.index(self.tournament.current_round)
        await self.message_rank.edit(embed=self.rank)
        await self.message_rounds.edit(embeds=self.rounds)
        self.update_button.disabled = True
        
    @disnake.ui.button(emoji = "⏮️", label = "Previous", style=disnake.ButtonStyle.primary, row = 1)
    async def previous(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            self.tournament.getPreviousRound()
            if self.tournament.rounds.index(self.tournament.current_round) == 0:
                self.previous.disabled = True
            self.next.disabled = False
            if self.tournament.nb_matchs_per_round == 1:
                self.match_selected = self.tournament.current_round.matches[0]
            else:
                self.match_selected = None
                
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "⏭️", label = "Next", style=disnake.ButtonStyle.primary, row = 1)
    async def next(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            self.tournament.getNextRound()
            if self.tournament.rounds.index(self.tournament.current_round) == len(self.tournament.rounds) - 1:
                self.next.disabled = True
            if self.tournament.rounds.index(self.tournament.current_round) > self.max_round: 
                self.update_button.disabled = False
            self.previous.disabled = False
            if self.tournament.nb_matchs_per_round == 1:
                self.match_selected = self.tournament.current_round.matches[0] 
            else:
                self.match_selected = None

        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "▶️", label = "Start", style=disnake.ButtonStyle.primary, row = 1)
    async def start(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        await self.update_dashboard(interaction)
        if self.is_admin(interaction):
            for i in range(self.tournament.nb_matchs_per_round):
                for j in range(2):
                    await self.tournament.current_round.matches[i].teams[j].move_to(self.voices[i][j])
                    
    @disnake.ui.button(emoji = "🔁", label = "Update", style=disnake.ButtonStyle.primary, row = 1)
    async def update_button(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            await self.update_infos()
        await self.update_dashboard(interaction)
        
    @disnake.ui.button(emoji = "❌", label = "End", style=disnake.ButtonStyle.danger, row = 1)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            await interaction.response.defer()
            await self.admin.send(embeds=self.embeds)
            for channel in self.category.channels:
                await channel.delete()
            await self.category.delete()
            await self.bot.change_presence(activity=disnake.Game(name='"/" -> commandes'))
            self.stop()
        else:
            await self.update_dashboard(interaction)      
 
    @disnake.ui.select(min_values = 1, max_values = 1, row = 2)
    async def match_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if self.is_admin(interaction):
            self.match_selected = self.tournament.current_round.matches[int(select.values[0][0])]
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
            team = self.match_selected.teams[0]
            team.reset_score()
            scores = select.values[0]
            team.addKills(int(scores[0]))
            team.addTurrets(int(scores[1]))
            team.addCS(int(scores[2]))
            self.update_button.disabled = False
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
            team = self.match_selected.teams[1]
            team.reset_score()
            scores = select.values[0]
            team.addKills(int(scores[0]))
            team.addTurrets(int(scores[1]))
            team.addCS(int(scores[2]))
            self.update_button.disabled = False
        await self.update_dashboard(interaction)
  
