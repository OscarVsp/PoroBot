from typing import List
import disnake
from .Embed import Embed
from enum import Enum

class State(Enum):
    CANCELLED = 0
    CONFIRMED = 1
    TIMEOUT = 2
    UNKOWN = 3

class ConfirmationView(disnake.ui.View):
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, timeout : int, color : disnake.Colour = disnake.Colour.default(), thumbnail : str = None):
        super().__init__(timeout=timeout)
        self.inter : disnake.Interaction = inter
        self.title : str = title
        self.message : str = message
        self.thumbnail : str = thumbnail if thumbnail else disnake.Embed.Empty
        self.color : disnake.Colour = color
        
        self.state : State = State.UNKOWN
        self.original_embeds : List[disnake.Embed] = []
        
    @property
    def embed(self) -> disnake.Embed:
        return Embed(
            title=self.title,
            description=self.message,
            thumbnail=self.thumbnail,
            color=self.color
        )
            
    async def send(self):
        if isinstance(self.inter, disnake.ApplicationCommandInteraction) or isinstance(self.inter, disnake.MessageInteraction):
            if self.inter.response.is_done():
                self.original_embeds = (await self.inter.original_message()).embeds
                await self.inter.edit_original_message(embeds=self.original_embeds+[self.embed], view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
        else:
            if self.inter.response.is_done():
                await self.inter.edit_original_message(embed=self.embed, view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
            
    async def update(self, inter : disnake.MessageInteraction = None):
        if inter == None:
            await self.inter.edit_original_message(
                embeds = self.original_embeds+ self.embed,
                view = self
            )
        else:
            if inter.response.is_done():
                await inter.edit_original_message(
                    embeds=self.original_embeds+[self.embed],
                    view=self
                )
            else:
                await inter.response.edit_message(
                    embeds=self.original_embeds+[self.embed],
                    view=self
                )

    @disnake.ui.button(label = "Confirmer", emoji="✅", style=disnake.ButtonStyle.green)
    async def confirm(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = State.CONFIRMED
        self.stop()
        
            
    @disnake.ui.button(label = "Annuler", emoji="❌", style=disnake.ButtonStyle.danger)
    async def cancel(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = State.CANCELLED
        self.stop()
        
    async def on_timeout(self) -> None:
        await self.inter.edit_original_message(embed=Embed(description="⭕ Timeout",color=disnake.Colour.dark_grey()))
        self.state = State.TIMEOUT
          
          

class ConfirmationReturnData:
    
    def __init__(self, confirmationView : ConfirmationView):
        self._state = confirmationView.state
        
    @property
    def is_ended(self) -> bool:
        return self._state != State.UNKOWN
              
    @property
    def is_confirmed(self) -> bool:
        return self._state ==  State.CONFIRMED
    
    @property
    def is_cancelled(self) -> bool:
        return self._state == State.CANCELLED
    
    @property
    def is_timeout(self) -> bool:
        return self._state == State.TIMEOUT
    
    def __bool__(self) -> bool:
        return self.is_confirmed
