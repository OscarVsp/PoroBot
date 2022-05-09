import disnake 
from disnake import ApplicationCommandInteraction
from utils.embed import new_embed
from utils import data
import asyncio
from random import shuffle, sample
from itertools import cycle
from math import ceil

class BangMenu(disnake.ui.View):
    
    
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=None)
        self.players = [Player(inter.author)]
        self.start =  False
        self.play.disabled = True
        self.interaction = None
        
    @property   
    def embed(self):
        embed = new_embed(
                title = "__**BANG - MENU**__",
                footer = "Au moins deux joueurs pour démarrer une partie.",
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
        
    @disnake.ui.button(emoji = "🍺", label = "Participer", style=disnake.ButtonStyle.primary)
    async def participer(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        if interaction.author in [m.member for m in self.players]:
            self.players.remove(next((p for p in self.players if p.member == interaction.author)))
            if len(self.players) < 2:
                self.play.disabled = True
        else: 
            self.players.append(Player(interaction.author))
            if len(self.players) >= 2:
                self.play.disabled = False
        await self.update(interaction)
        
    @disnake.ui.button(emoji = "▶️", label = "Jouer", style=disnake.ButtonStyle.primary)
    async def play(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.start = True
        self.interaction = interaction
        self.stop()
        
    @disnake.ui.button(emoji = "❌", label = "Stop", style=disnake.ButtonStyle.danger)
    async def arret(self, button: disnake.ui.Button, interaction : disnake.MessageInteraction):
        self.start = False
        self.interaction = interaction
        self.stop()
        
    """@disnake.ui.button(emoji = "🔁", label = "Reset", style=disnake.ButtonStyle.secondary)
    async def reste(self, button disnake.ui.button, interaction : disnake.MessageInteraction):
        for player"""
            
        
class BangGame(disnake.ui.View):
    def __init__(self, inter : ApplicationCommandInteraction, players : list[Player]):
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
        
    @property
    def score_tab(self):
        return 'TODO'
        
    @property
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
            thumbnail = self.lastCarte.image
            footer = f"{len(self.cartes)}/{self.max_value} cartes joueés"
        )
        
        
    async def next_turn(self, interaction : disnake.MessageInteraction):
        self.lastActivePlayer = self.activePlayer
        self.lastCarte = self.activeCarte
        self.activePlayer = next(self.players)
        self.activeCarte = sample(self.cartes)
        await interaction.response.edit_message(
            embed = self.embed,
            view = self
        )
        await self.activePlayer.send(self.activeCarte)
 
 class PlayerSelection(disnake.ui.Select):
     
    def __init__(self, game : BangGame, players : list[Player], activePlayer = Player, as_coeur : bool = False):
        self.game = game
        self.players = players
        super().__init__(
            placeholder = "C'est {activePlayer.display_name} qui a le paquet",
            min_values = 1,
            max_values = 1,
            options = [disnake.SelectOption(label=p.display_name) for p in players]
        )
        
    async def callback(self, interaction: disnake.MessageInteraction):
        await self.game.give_carte({self.players[self.values[0]]})

        
        
        
        
class Carte(object):
    """Cartes class
    
    Attributs:
        value (int):    The value of the card.
        color (str):    The color of the card

    Methodes:
        __init__():     Initialize a Carte object.
        isCarreau():    Is the card color "carreau".
        toString():     Make a string description of the card.
        toImage():      Get the "https" link to the image of the card.
    """
    def __init__(self, value, color):
        """Initialize a Carte object.

        Args:
            value (int): The value of the card
            color (str): The color of the card
        """
        self.value = value
        self.color = color

    def isCarreau(self):
        """Is the card color "carreau".

        Returns:
            boolean: True if the card color is "carreau", False otherwise.
        """
        return (self.color == "carreau")

    def __str__(self):
        """Make a string description of the card.

        Returns:
            str: The string description with the value and the color.
        """
        return f"{self.value} de {self.color}"
    
    @property
    def effet(self):
        if self.color == "pique":
            return f"Boit __{self.value}__ 🍺"
        elif self.color == "coeur":
            return f"Distribue __{self.value}__ 🍺"
        elif self.color == "carreau":
            return f"Boit __{self.value}__ 🍺 et est en mirror avec la dernière personne à avoir eu un carreau"
        elif self.color == "trefle":
            return f"Boit __{self.value}__ 🍺 et les personnes adjacentes boivent également {ceil(self.value/2)} 🍺"


    @property
    def image(self):
        """Get the "https" link to the image of the card.

        Returns:
            str: The "https" link to tho image on "Imgur".
        """
        return data.images.cards[self.color][self.value]
    
    @property
    def embed(self):
        return = new_embed(
            title = {self},
            thumbnail = self.image,
            fields = {
                'name' : "__Effet :__",
                'value' = f"{self.effet}"
            }
        )
    

class Player(object):
    """The "Player" class.
    
    Attributs:
        member (discord.Member):    The discord member.
        diplay_name (str):          The display name of the member.
        points (int):               The current points (for the partie).
        looses (int):               The number of looses (for the game).
        carreau (boolean):          If the player is currently on mirror.
        doubleCarreau (boolean):    If the player is currently on double-mirror.
        
    Methodes:
        __init__():                 Initialize the "Player" object.
        getCopy():                  Make a "deepcopy" copy of itself.
        takeCarte():                Received a card, actualize the score and check if the player is now on "mirror".
        isCarreau():                Check if the player is currently on mirror.
        isDoubleCarreau():          Check if the player is currently on double-mirror.
        reset():                    Reset all partie stats (points, carreau and doubleCarreau).
    """
    
    def __init__(self,member : disnake.Member, looses : int = 0):
        """Initialize the "Player" object.
        
        Args:
            member (discord.Member):    The discord member.
            looses (int, optional):     The intial looses (used to copy the player). Defaults to 0.
        """
        self.member = member
        self.display_name = member.display_name
        self.carreau = False
        self.doubleCarreau = False
        self.points = 0
        self.looses = looses

    def getCopy(self):
        """Make a "deepcopy" copy of itself.

        Returns:
            Player: The new Player object copied.
        """
        return Player(self.member,self.looses)
         
    def takeCarte(self,carte:Carte,mirror):
        """Received a card, actualize the score and check if the player is now on "mirror".

        Args:
            carte (Carte): The card received.
            mirror (list): The list of the current mirrors players.

        Returns:
            list[Player]: The new mirrors players.
        """
        
        
        self.points += carte.value
        if carte.isCarreau():
            if mirror[0] is not None:
                if mirror[0].doubleCarreau:
                    mirror[0].doubleCarreau = False
                else:
                    mirror[0].carreau = False
            if self.carreau:
                self.doubleCarreau = True
            else:
                self.carreau = True
            mirror[0] = mirror[1]
            mirror[1] = self
        return mirror

    @property
    def isCarreau(self):
        """Check if the player is currently on mirror.

        Returns:
            boolean: True if the player is on mirror, False otherwise.
        """
        return self.carreau

    @property
    def isDoubleCarreau(self):
        """Check if the player is currently on double-mirror.

        Returns:
            boolean: True if the player is on double-mirror, False otherwise.
        """
        return self.doubleCarreau

    def reset(self):
        """Reset all partie stats (points, carreau and doubleCarreau).
        """
        self.points = 0
        self.carreau = False
        self.doubleCarreau = False
        
    async def send(self,embed):
        await self.member.send(embed=embed)