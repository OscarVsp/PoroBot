import disnake 
from disnake import ApplicationCommandInteraction
from utils.embed import new_embed
from utils import data
import asyncio
from random import shuffle, sample
from itertools import cycle
from math import ceil
from .model import Player, Carte 

class BangMenu(disnake.ui.View):
    
    
    def __init__(self, author : disnake.member):
        super().__init__(timeout=None)
        self.players = [Player(author)]
        self.cancelled =  True
        self.number_players_min = 1
        self.interaction = None
        self.play.disabled = not len(self.players) >= self.number_players_min
        
    @property   
    def embed(self):
        embed = new_embed(
                title = "__**BANG - MENU**__",
                footer = f"Au moins {self.number_players_min} joueurs pour démarrer une partie.",
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
        if interaction.response.is_done():
            await interaction.response.edit_message(
                embed =self.embed,
                view = self
            )
        else:
            await interaction.response.send_message(
                embed =self.embed,
                view = self
            )
        
    @disnake.ui.button(emoji = "🍺", label = "Participer", style=disnake.ButtonStyle.primary)
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
        
    @disnake.ui.button(emoji = "▶️", label = "Jouer", style=disnake.ButtonStyle.primary)
    async def play(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.interaction = interaction
        self.stop()
        
    @disnake.ui.button(emoji = "❌", label = "Stop", style=disnake.ButtonStyle.danger)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.cancelled = True
        await interaction.delete_original_message()
        self.stop()
        
    """@disnake.ui.button(emoji = "🔁", label = "Reset", style=disnake.ButtonStyle.secondary)
    async def reste(self, button disnake.ui.button, interaction : disnake.MessageInteraction):
        for player"""
            
        
class BangGame(disnake.ui.View):
    def __init__(self, players : list[Player]):
        super().__init__(timeout=None)
        self.players = cycle(shuffle(players))
        self.max_value = 6
        self.cartes = [Carte(number+1,color) for number in range(self.max_value) for color in ["pique","coeur","carreau","trefle"]]
        self.lastCarte = None
        self.lastBangedPlayer = None
        self.lastActivePlayer = None
        self.mirror_players = [None,None]
        self.activePlayer = None
        self.activeCarte = None
        self.playerSelection = None
        
    @property
    def score_tab(self):
        return 'TODO'
        
    def embed(self, message : str = ""):
        return new_embed(
            name = "__**BANG - PARTIE**__",
            fields = [
                {
                    'name' : "__Dernière carte jouée :__",
                    'value' : f"**{self.lastCarte}**\n*{self.lastCarte.effet}*"
                },
                {
                    'name' : "__Score :__",
                    'value' : f"{self.score_tab}"
                },
                {
                    'name' : "__Tour en cours :__",
                    'value' : f"C'est a **{self.activePlayer.display_name}** de jouer !\n{message}"
                }
            ],
            thumbnail = self.lastCarte.image,
            footer = f"{len(self.cartes)}/{self.max_value} cartes joueés"
        )
        
        
    async def start_game(self, interaction : disnake.MessageInteraction):
        self.activePlayer = next(self.players)
        self.activeCarte = sample(self.cartes)
        self.playerSelection = PlayerSelection(self)
        self.add_item(self.playerSelection)
        await interaction.response.edit_message(
            embed = new_embed(
                name = "__**BANG - PARTIE**__",
                fields = [
                    {
                        'name' : "__Dernière carte jouée :__",
                        'value' : f"*Les cartes jouées s'afficheront ici*"
                    },
                    {
                        'name' : "__Score :__",
                        'value' : f"{self.score_tab}"
                    },
                    {
                        'name' : "__Tour en cours :__",
                        'value' : f"C'est a **{self.activePlayer.display_name}** de jouer !\n{message}"
                    }
                ],
                thumbnail = data.images.cards['back'],
                footer = f"{len(self.cartes)}/{self.max_value} cartes joueés"
            ),
            view = self
        )
        await self.activePlayer.send(self.activeCarte)
        
        
    async def play_turn(self, interaction : disnake.MessageInteraction, player : Player):
        self.mirror_players = player.takeCarte(self.activeCarte,self.mirror_players)
        self.lastBangedPlayer = player
        self.cartes.remove(self.activeCarte)
        self.lastActivePlayer = self.activePlayer
        self.lastCarte = self.activeCarte
        self.activePlayer = next(self.players)
        self.activeCarte = sample(self.cartes)
        self.remove_item(self.playerSelection)
        self.playerSelection = PlayerSelection(self)
        self.add_item(self.playerSelection)
        await interaction.response.edit_message(
            embed = self.embed(),
            view = self
        )
        await self.activePlayer.send(self.activeCarte)
        
    async def unautorized_interaction(self, interaction : disnake.MessageInteraction):
        await interaction.response.edit_message(
            embed = self.embed(f"⛔ *Ce n'est pas toi qui a les cartes * {interaction.author.mention} !")
        )
        
 
class PlayerSelection(disnake.ui.Select):
     
    def __init__(self, game : BangGame):
        self.game = game
        self.activePlayer = game.activePlayer
        self.players = game.players
        super().__init__(
            placeholder = "C'est {activePlayer.display_name} qui a le paquet de cartes",
            min_values = 1,
            max_values = 1,
            options = [disnake.SelectOption(label=p.display_name) for p in players]
        )
        
    async def callback(self, interaction: disnake.MessageInteraction):
        if interaction.author == self.activePlayer.member:
            await self.game.play_turn(interaction, {self.players[self.values[0]]})
        else:
            await self.game.unautorized_interaction(interaction)

        
        
        
