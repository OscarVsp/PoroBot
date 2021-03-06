import disnake 
from disnake import ApplicationCommandInteraction
from utils.FastEmbed import FastEmbed
from utils import data
from utils.tools import tracebackEx
import asyncio
from modules.LolPatchNoteScraper.PatchNote import PatchNote


drink_embed = FastEmbed(
        title = "__**:underage: RÈGLES DE L'ARAM À BOIRE ! :beers:**__",
        description = """✅ :arrow_right: Donner une gorgée :beers:
                         :o2: :arrow_right: Boire une gorgée :beers:
                         :vs: :arrow_right: ✅ ou :o2: en fonction.""",
        fields = [
            {
                'name' : "__Pendant la partie :__",
                'value' : """> 1️⃣ Faire un kill ...................................................... ✅1️⃣
                             > :two: Mourrir ............................................................. :o2:1️⃣
                             > :three: Toutes les 5 assist ......................................... ✅1️⃣
                             > :four: First blood ........................................................ :vs:1️⃣
                             > :five: Pentakill ............................................................ :vs::five:
                             > :six: Faire un kill dans la fontaine (et survivre) ✅:two: (:four:)
                             > :seven: Toucher le nexus ............................................ :o2:1️⃣
                             > :eight: Dans la fontaine sur l'écran de victoire .... ✅:three:"""
            },
            {
                'name' : "__Après la partie :__",
                'value' : """> 1️⃣ Perfect game (0 mort) ................................. ✅:five:
                             > :two: 100% kill participation ................................. ✅:five:
                             > :three: Perfect support (0 kill) ................................ ✅:three:
                             > :four: Abandon .......................................................... :o2::five:
                             > :five: Avoir tilt ........................................................... :o2::five:"""
            },
            {
                'name' : "__Spectateur :__",
                'value' : """> S'il y a un spectateur,celui-ci doit choisir un joueur avant la partie. Chaque fois que ce joueur doit ✅ ou :o2:, le spectateur fait de même.
                             > Celui-ci peut donner des gorgées à n'importe quel joueur et n'importe quel joueur pour lui donner des gorgées."""
                
            }
        ],
        thumbnail = data.images.poros.gragas
    )


        
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
        