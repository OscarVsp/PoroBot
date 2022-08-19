from typing import List
import disnake
from cogs.Lol.exceptions import SummonerNotFound
from cogs.Lol.watcher import CurrentGame, Summoner 
import modules.FastSnake as FS
from modules.LolPatchNoteScraper import PatchNote


drink_embed = FS.Embed(
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
        thumbnail = FS.Images.Poros.GRAGAS
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
            
        self.embed : disnake.Embed = FS.Embed(
            author_name = f"Patch {self.patch.season_number}.{self.patch.patch_number}",
            title = f"{self.patch.title}",
            description = self.patch.description,
            url = self.patch.link,
            image = self.patch.overview_image,
            thumbnail = FS.Images.Lol.LOGO,
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
        
        
        
class CurrentGameView(disnake.ui.View):
    
    def __init__(self, summoner_name : str):
        super().__init__(timeout=60*60)
        self.summoner_name : str = summoner_name
        self.current_summoner : Summoner = None
        self.current_player : CurrentGame.Participant = None
        self.live_game : CurrentGame = None
                
    async def start(self, inter : disnake.ApplicationCommandInteraction):
        try:
            self.current_summoner = await Summoner.by_name(self.summoner_name)
        except SummonerNotFound:
            await inter.edit_original_message(embed=FS.Embed(title="Invocateur inconnu", description=f"Le nom d'invocateur ***{self.summoner_name}*** ne correspond à aucun invocateur...", footer_text="Tu peux rejeter ce message pour le faire disparaitre"), view=None)
            await inter.delete_original_message(delay = 3)
            return
        
        await inter.edit_original_message(embeds=[await self.current_summoner.embed(force_update=True),FS.Embed(description=f"{FS.Emotes.LOADING} *Recherche de game en cours...*")])

        self.live_game = await self.current_summoner.currentGame()
        if self.live_game:  
            self.buttons : List[disnake.ui.Button] = []
            for i,team in enumerate(self.live_game.teams):
                for j,player in enumerate(team.participants):
                    name = player.summonerName
                    if len(name) > 8:
                        name = name[:8]
                    button = disnake.ui.Button(label=name,custom_id=f'{i}:{j}',emoji=player.championIcon)
                    button.callback = self.call_back
                    self.add_item(button)
                    self.buttons.append(button)
            self.current_player = next((p for p in self.live_game.participants if p.summonerName.lower() == self.summoner_name.lower() ), None)
            await self.update(inter)
            for participant in self.live_game.participants:
                await (await participant.summoner()).masteries()
        else:
            await inter.edit_original_message(embeds=[(await self.current_summoner.embed()),FS.Embed(description="*Pas de partie en cours*")])
            await inter.delete_original_message(delay=10)

        
        
                
    async def embeds(self) -> List[disnake.Embed]:
        game_embed = await self.live_game.embeds()
        return [game_embed[0],await self.current_player.embed()] +  game_embed[1:]
    
    async def update(self, inter : disnake.MessageInteraction):
        for button in self.buttons:
            button.disabled = (self.current_player.summonerName.lower().startswith(button.label.lower()))
        if inter.response.is_done():
            await inter.edit_original_message(embeds=await self.embeds(), view = self)
        else:
            await inter.response.edit_message(embeds=await self.embeds(), view = self)
                
                
    async def call_back(self, inter : disnake.MessageInteraction):
        await inter.response.defer()
        self.current_player = next((p for p in self.live_game.participants if p.summonerName.lower().startswith(inter.component.label.lower()) ), None)
        await self.update(inter)

    
    
        