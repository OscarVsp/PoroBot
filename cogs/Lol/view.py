import disnake 
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from utils import data
from utils.tools import tracebackEx
import asyncio
from modules.LolPatchNoteScraper.PatchNote import PatchNote


drink_embeds = [
    FastEmbed(
        title = "__**:underage: RÈGLES DE L'ARAM À BOIRE ! :beers:**__",
        description = """:white_check_mark: :arrow_right: Donner une gorgée :beers:
                        :o2: :arrow_right: Boire une gorgée :beers:
                        :vs: :arrow_right: :white_check_mark: ou :o2: en fonction."""
    ),
    FastEmbed(
        title = "__Pendant la partie :__",
        description = """:black_medium_small_square::one: Faire un kill ...................................................... :white_check_mark::one:
                         :black_medium_small_square::two: Mourrir ............................................................. :o2::one:
                         :black_medium_small_square::three: Toutes les 5 assist ......................................... :white_check_mark::one:
                         :black_medium_small_square::four: First blood ........................................................ :vs::one:
                         :black_medium_small_square::five: Pentakill ............................................................ :vs::five:
                         :black_medium_small_square::six: Faire un kill dans la fontaine (et survivre) :white_check_mark::two: (:four:)
                         :black_medium_small_square::seven: Toucher le nexus ............................................ :o2::one:
                         :black_medium_small_square::eight: Dans la fontaine sur l'écran de victoire .... :white_check_mark::three:"""
    ),
    FastEmbed(
        title = "__Après la partie :__",
        description = """:black_medium_small_square::one: Perfect game (0 mort) ................................. :white_check_mark::five:
                         :black_medium_small_square::two: 100% kill participation ................................. :white_check_mark::five:
                         :black_medium_small_square::three: Perfect support (0 kill) ................................ :white_check_mark::three:
                         :black_medium_small_square::four: Abandon .......................................................... :o2::five:
                         :black_medium_small_square::five: Avoir tilt ........................................................... :o2::five:"""
    ),
    FastEmbed(
        title = "__Spectateur :__",
        description = """S'il y a un spectateur,celui-ci doit choisir un joueur avant la partie. Chaque fois que ce joueur doit :white_check_mark: ou :o2:, le spectateur fait de même.
                         Celui-ci peut donner des gorgées à n'importe quel joueur et n'importe quel joueur pour lui donner des gorgées."""
    )
]


        
class PatchNoteView(disnake.ui.View):
    
    def __init__(self, inter : disnake.ApplicationCommandInteraction, previous : int = 0, lang : str = None):
        super().__init__(timeout=60*10)
        self.inter : disnake.ApplicationCommandInteraction = inter
        
        if lang != None and lang in PatchNote.langs:
            self.patch : PatchNote = PatchNote(previous = previous, lang = lang)
        elif inter.locale == disnake.Locale.fr:
            self.patch : PatchNote = PatchNote(previous = previous, lang = 'fr-fr')
        else:
            self.patch : PatchNote = PatchNote(previous = previous, lang = 'en-gb')
            
        self.embed : disnake.Embed = FastEmbed(
            author_name = f"Patch {self.patch.season_number}.{self.patch.patch_number}",
            title = f"{self.patch.title}",
            description = self.patch.description,
            url = self.patch.link,
            image = self.patch.overview_image,
            thumbnail = "https://i.imgur.com/0Fyu6yl.png",
            color = disnake.Colour.dark_blue()      
        )
        self.add_item(
            disnake.ui.Button(
                style = disnake.ButtonStyle.link,
                url = self.patch.link, 
                label = f"Patch {self.patch.season_number}.{self.patch.patch_number}",
                emoji = "<:Lol:658237632786071593>"
            )
        )

        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
        