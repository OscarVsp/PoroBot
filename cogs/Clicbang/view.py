import disnake 
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from utils import data
import asyncio
from random import shuffle, choice
from itertools import cycle
from .model import Player, Carte, regles
from typing import List
from operator import attrgetter

class BangMenu(disnake.ui.View):
      
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=60*10)
        self.players = [Player(inter.author)]
        self.cancelled = False
        self.number_players_min = 1
        self.interaction = None
        self.inter = inter
        self.play.disabled = len(self.players) < self.number_players_min
        
    @property   
    def embed(self):
        embed = FastEmbed(
                title = "__**BANG - MENU**__",
                footer_text= f"Au moins {self.number_players_min} joueurs pour démarrer une partie.",
                thumbnail = data.images.bang_6
        )
        if len(self.players) != 0:
            embed.add_field(
                name = "__Joueurs : __",
                value = "\n".join([p.display_name for p in self.players])
            )
        else:
            embed.add_field(
                name = "__Joueurs : __",
                value = "*Aucun joueur dans la partie*"
            )
        return embed
            
    async def update(self, interaction : disnake.MessageInteraction):
        await interaction.response.edit_message(
                embed =self.embed,
                view = self
            )
        
    @disnake.ui.button(emoji = "➕", label = "Participer", style=disnake.ButtonStyle.primary, row = 1)
    async def participer(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if interaction.author in [m.member for m in self.players]:
            self.players.remove(next((p for p in self.players if p.member == interaction.author)))
            if len(self.players) < self.number_players_min:
                self.play.disabled = True
        else: 
            self.players.append(Player(interaction.author))
            if len(self.players) >= self.number_players_min:
                self.play.disabled = False
        await self.update(interaction)
        
    @disnake.ui.button(emoji = "📜", label = "Règles", style = disnake.ButtonStyle.secondary, row = 1)
    async def regle(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await self.update(interaction)
        await interaction.author.send(embed = regles)
        
    @disnake.ui.button(emoji = "▶", label = "Jouer", style=disnake.ButtonStyle.primary, row = 2)
    async def play(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.interaction = interaction
        self.stop()
        
    @disnake.ui.button(emoji = "❌", label = "Stop", style=disnake.ButtonStyle.danger, row = 2)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.cancelled = True
        await self.inter.delete_original_message()
        self.stop()
        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
        
class BangGame(disnake.ui.View):
    def __init__(self, inter : ApplicationCommandInteraction, players : List[Player], max_value : int):
        super().__init__(timeout=60*60)
        self.inter = inter
        self.players = players
        self.max_value = max_value
        for player in self.players:
            self.player_selection.add_option(label = player.display_name)
        
        
    @property
    def score_tab(self):
        player_lines = []
        for player in self.players:
            if player == self.activePlayer:
                line = ":small_orange_diamond:"
            else:
                line = ":black_medium_small_square:"
            line += f"**{player.display_name}** : {player.points}"
            if player.isCarreau:
                line += ":diamonds:"
            if player.isDoubleCarreau:
                line += ":diamonds:"
            player_lines.append(line)
        return "/n".join(player_lines)
    
    @property
    def footer(self):
        return f"{self.max_value*4 - len(self.cartes)}/{self.max_value*4} cartes jouées"
        
    def embed(self, message : str = ""):
        embed = FastEmbed(
            title = "__**BANG - PARTIE**__"
        )
        if self.lastCarte == None:
            embed.add_field(
                name = '__Dernière carte jouée :__',
                value = "*Les cartes jouées s'afficheront ici*",
                inline = False
            )
            embed.set_thumbnail(url = data.images.cards['back'])
        else:
            embed.add_field(
                name = '__Dernière carte jouée :__',
                value = f"**{self.lastCarte}**\n*{self.lastCarte.effet}*",
                inline = False
            )
            embed.set_thumbnail(url = self.lastCarte.image)
        embed.add_field(
            name = '__Score :__',
            value = f"{self.score_tab}",
                inline = False
        )
        if self.looser != None:
            embed.add_field(
                name = "__La partie est finie !__",
                value = f"{self.looser.display_name} perd avec {self.looser.points} points",
                inline = False
            )
        else:
            embed.add_field(
                name = "__Tour en cours :__",
                value = f"C'est à **{self.activePlayer.display_name}** de jouer !\n{message}",
                inline = False 
            )
            embed.set_footer(text = self.footer)
        return embed
        
        
    async def start_game(self, interaction : disnake.MessageInteraction):
        self.reset_all_players()
        shuffle(self.players)
        self.players_iter = cycle(self.players)
        self.cartes = [Carte(number+1,color) for number in range(self.max_value) for color in ["pique","coeur","carreau","trefle"]]
        self.lastCarte = None
        self.lastBangedPlayer = None
        self.lastActivePlayer = None
        self.looser = None
        self.mirror_players = [None,None]
        
        self.activePlayer = next(self.players_iter)
        self.player_selection.placeholder = f"{self.activePlayer.display_name} : Sélectionne la cible du bang"
        self.activeCarte = choice(self.cartes)
        await interaction.response.edit_message(
            embed = self.embed(),
            view = self
        )
        await self.activePlayer.send(self.activeCarte)
        
        
    async def play_turn(self, interaction : disnake.MessageInteraction, player : Player):
        self.mirror_players = player.takeCarte(self.activeCarte,self.mirror_players)
        self.lastBangedPlayer = player
        self.cartes.remove(self.activeCarte)
        self.lastActivePlayer = self.activePlayer
        self.lastCarte = self.activeCarte
        if len(self.cartes) > 0:
            self.activePlayer = next(self.players_iter)
            self.activeCarte = choice(self.cartes)
            self.player_selection.placeholder = f"{self.activePlayer.display_name} : Sélectionne la cible du bang"
            await interaction.response.edit_message(
                embed = self.embed(),
                view = self
            )
            await self.activePlayer.send(self.activeCarte)
        else:
            self.looser = max(self.players, key=attrgetter('points'))
            await interaction.response.edit_message(
                embed = self.embed(),
                view = self
            )     
        
    def reset_all_players(self):
        for player in self.players:
            player.reset()
        
    async def unautorized_interaction(self, interaction : disnake.MessageInteraction):
        await interaction.response.edit_message(
            embed = self.embed(f"⛔ *Ce n'est pas toi qui a les cartes * {interaction.author.mention} !")
        )
        
    @disnake.ui.select(min_values = 1, max_values = 1, row = 1)
    async def player_selection(self, select : disnake.ui.Select, interaction : disnake.MessageInteraction):
        if interaction.author == self.activePlayer.member:
            await self.play_turn(interaction, next((p for p in self.players if p.display_name == select.values[0])))
        else:
            await self.unautorized_interaction(interaction)
    
    @disnake.ui.button(emoji = "📜", label = "Règle", style = disnake.ButtonStyle.secondary, row = 2)
    async def regle(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer(with_message=False)
        await interaction.author.send(embed = regles)
        
    @disnake.ui.button(emoji = "🔁", label = "Replay", style = disnake.ButtonStyle.primary, row = 2)
    async def replay(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        if self.playerSelection in self.children:
            self.remove_item(self.playerSelection) 
        await self.start_game(interaction)
        
    @disnake.ui.button(emoji = "❌", label = "Stop", style = disnake.ButtonStyle.danger, row = 2)
    async def arret(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await self.inter.delete_original_message()
        self.stop()
        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
        
        