import disnake 
from disnake import ApplicationCommandInteraction
from random import randint,choices,sample
from utils.embed import new_embed
from utils import data

class PoroFeed(disnake.ui.View):
    
    images = [
            "https://i.imgur.com/Eex5g5J.png",
            "https://i.imgur.com/52LLvqI.png",
            "https://i.imgur.com/2vEGssv.png",
            "https://i.imgur.com/PcXqiub.png",
            "https://i.imgur.com/7ohi1cB.png",
            "https://i.imgur.com/VBmrv8w.png",
            "https://i.imgur.com/7bIdncF.png",
            "https://i.imgur.com/gQ79HSq.png",
            "https://i.imgur.com/2gBVwgr.png",
            "https://i.imgur.com/LGM3liY.png",
            "https://i.imgur.com/sGvrPcj.png"
            ]
    
    
    def __init__(self, inter : ApplicationCommandInteraction):
        super().__init__(timeout=10)
        self.inter = inter
        self.counter = 0


    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # note: The name of the function does not matter to the library
    @disnake.ui.button(emoji = "<:porosnack:908477364135161877>", style=disnake.ButtonStyle.primary)
    async def feed(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        if self.counter < 9:
            self.counter += 1
            await interaction.response.edit_message(
                embed = new_embed(
                    description="Continue à nourrir le poro !", 
                    image=PoroFeed.images[self.counter], 
                    footer = f"{self.counter}/10"),
                view=self)
        else:
            self.counter += 1
            button.disabled = True
            await interaction.response.edit_message(
                embed = new_embed(
                    description="*#Explosion de poros*", 
                    image=PoroFeed.images[self.counter]),
                view=self)
        
    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
        