import disnake 
from disnake import ApplicationCommandInteraction
from random import choices
from utils.embed import new_embed
from utils import data
import asyncio

class ClashView(disnake.ui.View):
    
    def __init__(self):
        super().__init__(timeout=600)

    @disnake.ui.button(label = "OP.GG", emoji = "<:opgg:0000>", style=disnake.ButtonStyle.link)
    async def opgg(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        pass
    
    async def set_opgg(self, link : str ) -> None:
        self.opgg.url = link
                
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()