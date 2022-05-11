import disnake 
from disnake import ApplicationCommandInteraction
from utils.embed import new_embed
from utils import data
from utils.paginator import Paginator_short
from utils.tools import tracebackEx
import asyncio
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify


drink_embeds = [
    new_embed(
        title = "__**:underage: RÈGLES DE L'ARAM À BOIRE ! :beers:**__",
        description = """:white_check_mark: :arrow_right: Donner une gorgée :beers:
                        :o2: :arrow_right: Boire une gorgée :beers:
                        :vs: :arrow_right: :white_check_mark: ou :o2: en fonction."""
    ),
    new_embed(
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
    new_embed(
        title = "__Après la partie :__",
        description = """:black_medium_small_square::one: Perfect game (0 mort) ................................. :white_check_mark::five:
                         :black_medium_small_square::two: 100% kill participation ................................. :white_check_mark::five:
                         :black_medium_small_square::three: Perfect support (0 kill) ................................ :white_check_mark::three:
                         :black_medium_small_square::four: Abandon .......................................................... :o2::five:
                         :black_medium_small_square::five: Avoir tilt ........................................................... :o2::five:"""
    ),
    new_embed(
        title = "__Spectateur :__",
        description = """S'il y a un spectateur,celui-ci doit choisir un joueur avant la partie. Chaque fois que ce joueur doit :white_check_mark: ou :o2:, le spectateur fait de même.
                         Celui-ci peut donner des gorgées à n'importe quel joueur et n'importe quel joueur pour lui donner des gorgées."""
    )
]



headers = {'Accept': 'application/json'}
base_url = "https://www.leagueoflegends.com/page-data/fr-fr"
patch_notes_url = '/news/tags/patch-notes/'
end_url = "page-data.json"
view_url = "https://www.leagueoflegends.com/fr-fr"

        
class PatchNote:
    
    def __init__(self):
        
        try:
            articles = requests.get(base_url+patch_notes_url+end_url, headers=headers).json()
        except (Exception):
            raise PatchNoteException(f"Patch notes list request error for url: {base_url+patch_notes_url+end_url}")
        
        try:
            last_article_url = articles['result']['data']['articles']['nodes'][0]['url']['url']
        except (Exception):
            raise PatchNoteException(f"Patch note url not found in patch notes list data")
        
        self.link = view_url + last_article_url
        
        try:
            last_article_data = requests.get(base_url+last_article_url+end_url, headers=headers).json()
        except (Exception):
            raise PatchNoteException(f"Last patch request error for url: {base_url+last_article_url+end_url}")
        
        try:
            last_article = last_article_data['result']['data']['all']['nodes'][0]
        except (Exception):
            raise PatchNoteException(f"Last patch note data not found")
        
        try:
            self.title = last_article['description']
        except (Exception):
            raise PatchNoteException(f"Last patch note title not found")
        
        soup = BeautifulSoup(last_article['patch_notes_body'][0]['patch_notes']['html'], 'html.parser')

        try:
            self.description : str = markdownify(str(soup.blockquote),  heading_style="ATX").replace('>','')
        except (Exception):
            self.description : str = ":warning: No description available :warning:"
        
        try:
            self.image : str = soup.find(attrs={"class": "skins cboxElement"}).img.get('src')
        except (Exception):
            self.image : str = 'https://images.contentstack.io/v3/assets/blt731acb42bb3d1659/bltf06237d0ebbe32e0/5efc23abee48da0f762bc2f2/LOL_PROMOART_4.jpg'
        
        
        self.embed : Embed = new_embed(
            title = self.title,
            description = self.description,
            url = self.link,
            image = self.image,
            color = disnake.Colour.dark_blue()        
        )
        
class PatchNoteException(Exception):
        
    def __init__(self, msg : str = None):
        super().__init__(msg)


        