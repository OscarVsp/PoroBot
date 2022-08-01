from dataclasses import MISSING
from urllib import response
import disnake
from typing import Tuple, Union
from .FastEmbed import FastEmbed
from .data import color


    

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
        
        self.is_confirmed : bool = False
            
    async def send(self):
        if self.is_application_interaction:
            if self.inter.response.is_done():
                self.original_embeds = (await self.inter.original_message()).embeds
                if len(self.original_embeds) > 0:
                    await self.inter.edit_original_message(embeds=self.original_embeds+[self.embed], view=self)
                else:
                    await self.inter.edit_original_message(embed=self.embed, view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
        elif self.is_view_interaction:
            self.original_embeds = self.inter.message.embeds
            if len(self.original_embeds) > 0:
                await self.inter.response.edit_message(embeds=self.original_embeds+[self.embed], view=self)
            else:
                await self.inter.response.edit_message(embed=self.embed, view=self)

        
    async def cancel(self, interaction : disnake.MessageInteraction):
        self.stop()
        await self.clear_message(interaction)
        
    async def validate(self, interaction : disnake.MessageInteraction):
        self.is_confirmed = True
        self.stop()
        await self.clear_message(interaction)
        
    async def on_timeout(self) -> None:
        await self.clear_message(self.inter)
            
    async def clear_message(self, interaction : disnake.Interaction) -> None:
        await interaction.response.defer()

          
async def confirmation(
    inter : disnake.Interaction,
    title : str = "Confirmation",
    message : str = "Confirmer l'action ?",
    timeout : int = 180,
    confirmationLabel : str = "Confirmer",
    cancelLabel : str = "Annuler") -> bool:
    confirmationView = ConfirmationView(inter=inter, title=title, message=message, timeout=timeout, confirmationLabel=confirmationLabel, cancelLabel=cancelLabel)
    await confirmationView.send()
    await confirmationView.wait()
    return confirmationView.is_confirmed