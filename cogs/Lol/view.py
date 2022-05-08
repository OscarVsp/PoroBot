import disnake 
from disnake import ApplicationCommandInteraction
from random import choices
from utils.embed import new_embed
from utils.paginator import Paginator
import asyncio

class DrinkView(Paginator):
    def __init__(self, inter : ApplicationCommandInteraction):
        self.pre_embed = new_embed(
            title = "__**:underage: RÈGLES DE L'ARAM À BOIRE ! :beers:**__"
        )
        self.embeds = [
            new_embed(
                title="**__Legende :__**",
                description=""":white_check_mark: :arrow_right: Donner une gorgée :beers:
                               :o2: :arrow_right: Boire une gorgée :beers:
                               :vs: :arrow_right: :white_check_mark: ou :o2: en fonction."""
            ),
            new_embed(
                title="**__Pendant la partie :__**",
                description=""":black_medium_small_square::one: Faire un kill ...................................................... :white_check_mark::one:
                         :black_medium_small_square::two: Mourrir ............................................................. :o2::one:
                         :black_medium_small_square::three: Toutes les 5 assist ......................................... :white_check_mark::one:
                         :black_medium_small_square::four: First blood ........................................................ :vs::one:
                         :black_medium_small_square::five: Pentakill ............................................................ :vs::five:
                         :black_medium_small_square::six: Faire un kill dans la fontaine (et survivre) :white_check_mark::two: (:four:)
                         :black_medium_small_square::seven: Toucher le nexus ............................................ :o2::one:
                         :black_medium_small_square::eight: Dans la fontaine sur l'écran de victoire .... :white_check_mark::three:""",
            ),
            new_embed(
                title="**__Après la partie :__**",
                description=""":black_medium_small_square::one: Perfect game (0 mort) ................................. :white_check_mark::five:
                         :black_medium_small_square::two: 100% kill participation ................................. :white_check_mark::five:
                         :black_medium_small_square::three: Perfect support (0 kill) ................................ :white_check_mark::three:
                         :black_medium_small_square::four: Abandon .......................................................... :o2::five:
                         :black_medium_small_square::five: Avoir tilt ........................................................... :o2::five:""",
            ),
            new_embed(
                title="**__Spectateur :__**",
                description="""S'il y a un spectateur,celui-ci doit choisir un joueur avant la partie. Chaque fois que ce joueur doit :white_check_mark: ou :o2:, le spectateur fait de même. Celui-ci peut donner des gorgées à n'importe quel joueur et n'importe quel joueur pour lui donner des gorgées.""",
            )
        ]
        
        super().__init__(inter, self.embeds, self.pre_embed, timeout=1200)
        