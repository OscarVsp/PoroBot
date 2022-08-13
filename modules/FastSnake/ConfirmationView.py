import asyncio
from typing import List, Union
import disnake
from .Embed import Embed
from enum import Enum

class ViewState(Enum):
    CANCELLED = 0
    CONFIRMED = 1
    TIMEOUT = 2
    UNKOWN = 3
    
Target = Union[disnake.Interaction,disnake.TextChannel,disnake.Message, disnake.ModalInteraction]

class ConfirmationView(disnake.ui.View):
    
    def __init__(self, target : Target, title : str, description : str, timeout : int, color : disnake.Colour = disnake.Colour.default(), thumbnail : str = None):
        super().__init__(timeout=timeout)
        self.target : Target = target
        self.message_to_delete : disnake.Message = None
        self.title : str = title
        self.description : str = description
        self.thumbnail : str = thumbnail if thumbnail else disnake.Embed.Empty
        self.color : disnake.Colour = color
        
        self.state : ViewState = ViewState.UNKOWN
        self.original_embeds : List[disnake.Embed] = []
        
    @property
    def embed(self) -> disnake.Embed:
        return Embed(
            title=self.title,
            description=self.description,
            thumbnail=self.thumbnail,
            color=self.color
        )
            
    async def send(self):
        if isinstance(self.target, disnake.ApplicationCommandInteraction) or isinstance(self.target, disnake.MessageInteraction) or isinstance(self.target,disnake.ModalInteraction):
            if self.target.response.is_done():
                self.original_embeds = (await self.target.original_message()).embeds
                await self.target.edit_original_message(embeds=self.original_embeds+[self.embed], view=self)
            else:
                await self.target.response.send_message(embed=self.embed, view=self, ephemeral=True)
        elif isinstance(self.target, disnake.TextChannel):
            self.message_to_delete = await self.target.send(embed=self.embed, view=self)
        elif isinstance(self.target, disnake.Message):
            self.message_to_delete = await self.target.channel.send(embed=self.embed,view=self)
        else:
            if self.target.response.is_done():
                await self.target.edit_original_message(embed=self.embed, view=self)
            else:
                await self.target.response.send_message(embed=self.embed, view=self, ephemeral=True)
            
    async def update(self, inter : disnake.MessageInteraction):
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
            
    async def end(self) -> None:
        self.stop()
        if self.message_to_delete:
            await self.message_to_delete.delete()

    @disnake.ui.button(label = "Confirmer", emoji="✅", style=disnake.ButtonStyle.green)
    async def confirm(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CONFIRMED
        await self.end()
        
    @disnake.ui.button(label = "Annuler", emoji="❌", style=disnake.ButtonStyle.danger)
    async def cancel(self, button : disnake.ui.Button, interaction : disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CANCELLED
        await self.end()
        
    async def on_timeout(self) -> None:
        self.state = ViewState.TIMEOUT
        await self.end()
          
          

class ConfirmationReturnData:
    
    def __init__(self, confirmationView : ConfirmationView):
        self._state = confirmationView.state
        
    @property
    def is_ended(self) -> bool:
        return self._state != ViewState.UNKOWN
              
    @property
    def is_confirmed(self) -> bool:
        return self._state ==  ViewState.CONFIRMED
    
    @property
    def is_cancelled(self) -> bool:
        return self._state == ViewState.CANCELLED
    
    @property
    def is_timeout(self) -> bool:
        return self._state == ViewState.TIMEOUT
    
    def __bool__(self) -> bool:
        return self.is_confirmed
