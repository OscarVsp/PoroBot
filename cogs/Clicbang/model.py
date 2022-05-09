from utils import data
from utils.embed import new_embed
import disnake
from math import ceil

regles = new_embed(
    title = ":scroll: __**REGLES DU BANG**__ :scroll:",
    description = """Ce jeu reprend le principe de la roulette russe, avec des cartes. Chacun à son tour, on sera maitre du jeu et on tirera une carte (distribué automatiquement par le bot en message privé). Le nombre indiqué sur la carte correspond à la position de l'unique balle dans le barillet, et donc le nombre de *"coup à tiré"* avant que la balle sorte.
                     Le maitre du jeu choisit alors un autre joueur sur qui tirer, et annonce le résultat du tire (à faire oralement):
                     :arrow_right: **"Bang"** si la carte est un :one:, puisque c'est le premier coup tiré.
                     :arrow_right: **"Clic"** sinon, et le "pistolet" va au joueur ciblé.
                     Un joueur visé par un **"Clic"** choisit à son tour une cible, et le maitre du jeu annonce de nouveau le résultat (puisqu'il est le seul à connaitre la carte). Le *"pistolet"* va donc passer de joueur en joueur jusqu'à ce que le nombre de coups tirés soit égal au numéro sur la carte et donc que le maitre du jeu annonce **"Bang"**.
                     ▪
                     Lorsque cela se produit, le maitre du jeu révèle la carte et la donne au joueur victime du **"Bang"** en guise de balle (le maitre du jeu doit sélectionner la cible du **"Bang"** sous le message). L'effet dépend de la couleur de la carte, et le nombre de :beer: du numéro de la carte (l'effet est rappelé par le bot à chaque fois) :
                     :spades: Pique : Boit les :beer:.
                     :hearts: Coeur : Distribue les :beer: (garde la carte).
                     :clubs: Trefle : Boit les :beer: et les deux joueurs adjacents boivent la moitié (arrondit vers le haut).
                     :diamonds: Carreau : Boit les :beer: et les deux derniers joueurs à avoir eu un carreau sont en miroir.
                     ▪
                     Une fois la carte distribuée, le maitre du jeu passe le paquet de cartes au joueur à sa droite, qui devient le nouveau maitre du jeu (automatiquement fait par le bot). Le paquet tourne ainsi jusqu'à son épuisement.
                     Un joueur peut se prendre lui-même pour cible autant de fois qu'il se souhaite, à condition qu'il ne soit pas le maitre du jeu.
                     À la fin de la partie, le joueur ayant accumulé le plus de points (valeur cumulée des cartes en sa possession) est désigné perdant et prend un affond final."""
)
        
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
            return f"Boit **{self.value}** 🍺"
        elif self.color == "coeur":
            return f"Distribue **{self.value}** 🍺"
        elif self.color == "carreau":
            return f"Boit **{self.value}** 🍺\net est en mirror avec la dernière personne à avoir eu un :diamonds:"
        elif self.color == "trefle":
            return f"Boit **{self.value}** 🍺\net les personnes adjacentes boivent également **{ceil(self.value/2)}** 🍺"


    @property
    def image(self):
        """Get the "https" link to the image of the card.

        Returns:
            str: The "https" link to tho image on "Imgur".
        """
        return data.images.cards[self.color][self.value-1]
    
    @property
    def embed(self):
        return new_embed(
            title = f"{self}",
            thumbnail = self.image,
            fields = [{
                'name' : "__Effet :__",
                'value' : f"*{self.effet}*"
            }]
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
        
    async def send(self,carte):
        await self.member.send(embed=carte.embed)