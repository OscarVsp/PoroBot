import asyncio
from dataclasses import MISSING
from enum import Enum
from urllib import response
import disnake
from typing import Tuple, Union, List

from pydantic import TimeError
from .FastEmbed import FastEmbed
from .data import color

class State(Enum):
    CANCELLED = 0
    CONFIRMED = 1
    TIMEOUT = 2
    UNKOWN = 3


class ConfirmationStatus:
    
    def __init__(self, status : int):
        self.status : int = status
    
    def __bool__(self) -> bool:
        return self.status == State.CONFIRMED
    
    @property
    def is_confirmed(self) -> bool:
        return self.status == State.CONFIRMED
    
    @property
    def is_cancelled(self) -> bool:
        return self.status == State.CANCELLED
    
    @property
    def is_timeout(self) -> bool:
        return self.status == State.TIMEOUT
    
        
    

class ConfirmationView(disnake.ui.View):
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, timeout : int, confirmationLabel : str, cancelLabel : str):
        super().__init__(timeout=timeout)
        self.inter : disnake.Interaction = inter
        self.is_application_interaction : bool = isinstance(inter, disnake.ApplicationCommandInteraction)
        self.is_view_interaction : bool = isinstance(inter, disnake.MessageInteraction)
        
        confirmation_button = disnake.ui.Button(label = confirmationLabel, emoji="✅", style=disnake.ButtonStyle.green)
        confirmation_button.callback = self.validate
        cancel_button = disnake.ui.Button(label = cancelLabel, emoji = "❌", style= disnake.ButtonStyle.danger)
        cancel_button.callback = self.cancel
        
        self.add_item(confirmation_button)
        self.add_item(cancel_button)
        
        self.embed = FastEmbed(
            title=title,
            description=message,
            color=color.gris
        )

        self.state : ConfirmationStatus = ConfirmationStatus(State.UNKOWN)
            
    async def send(self):
        if self.is_application_interaction:
            if self.inter.response.is_done():
                original_embeds = (await self.inter.original_message()).embeds
                if len(self.original_embeds) > 0:
                    await self.inter.edit_original_message(embeds=original_embeds+[self.embed], view=self)
                else:
                    await self.inter.edit_original_message(embed=self.embed, view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
        elif self.is_view_interaction:
            original_embeds = self.inter.message.embeds
            if len(self.original_embeds) > 0:
                await self.inter.response.edit_message(embeds=original_embeds+[self.embed], view=self)
            else:
                await self.inter.response.edit_message(embed=self.embed, view=self)

        
    async def cancel(self, interaction : disnake.MessageInteraction):
        self.state.status = State.CANCELLED
        self.stop()
        await interaction.response.defer()
        
    async def validate(self, interaction : disnake.MessageInteraction):
        self.state.status = State.CONFIRMED
        self.stop()
        await interaction.response.defer()
        
    async def on_timeout(self) -> None:
        self.state.status = State.TIMEOUT
          
async def confirmation(
    inter : disnake.Interaction,
    title : str = "Confirmation",
    message : str = "Confirmer l'action ?",
    timeout : int = 180,
    confirmationLabel : str = "Confirmer",
    cancelLabel : str = "Annuler") -> ConfirmationStatus:
    """|coro|\n
    Send a confirmation view linked to the interaction.
    The interaction can be either an `ApplicationCommandInteraction` or a `MessageInteraction`.
    
    If the interaction of a `ApplicationCommandInteraction` has not been answered yet, the confirmation view is send using `ephemeral=True`.
    If the interaction has already been answered, or in the case of a `MessageInteraction`, the embeds of the original_message are kept and the confirmation view embed is simply added at the end of the list.
    
    At the end of the confirmation, the interaction is defer, but the embeds and views are not removed yet and should be explicitly dealt with during a following `"edit_original_message"` (e.g. `"view=None"` to remove the confirmation view).

    Parameters
    ----------
        inter (`disnake.Interaction`):
            The interaction for which the confirmation occurs.
        title (`str`, `optional`): 
            Title of the confirmation embed.
            Defaults to `"Confirmation"`.
        message (`str`, `optional`): 
            Message of the confirmation embed.
            Defaults to `"Confirmer l'action ?"`.
        timeout (`int`, `optional`): 
            The timeout for the user to answer to confirmation.
            Defaults to `180`.
        confirmationLabel (`str`, `optional`): 
            The label for the confirmation button.
            Defaults to `"Confirmer"`.
        cancelLabel (`str`, `optional`): 
            The label for the cancel button.
            Defaults to `"Annuler"`.

    Returns
    --------
        `ConfirmationStatus`: 
            `State.CONFIRMED` (`=True`) if the user has confirmed the action.
            `State.CANCELLED` (`=False`) if the user has cancelled the action.
            `State.TIMEOUT` (`=False`) if the user has not answered the action before timeout.
    """
    confirmationView = ConfirmationView(inter=inter, title=title, message=message, timeout=timeout, confirmationLabel=confirmationLabel, cancelLabel=cancelLabel)
    await confirmationView.send()
    await confirmationView.wait()
    return confirmationView.state