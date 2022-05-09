from utils import data
from utils.embed import new_embed
import disnake
        
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
        return new_embed(
            title = {self},
            thumbnail = self.image,
            fields = {
                'name' : "__Effet :__",
                'value' : f"{self.effet}"
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