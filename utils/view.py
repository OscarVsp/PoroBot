from types import coroutine
import disnake
from typing import Optional,List,Union
from .FastEmbed import FastEmbed
from .data import color

class ConfirmationView(disnake.ui.View):
    
    def __init__(self, inter : disnake.Interaction, callback : coroutine, callback_args : dict = {}, target : Union[disnake.TextChannel,disnake.User] = None, title : str = "Confirmation", message : str = "Confirmer l'action ?", ephemeral : bool = True, timeout : int = 180):
        super().__init__(timeout=timeout)
        self.inter : disnake.Interaction = inter
        self.target : Union[disnake.TextChannel,disnake.User] = target
        self.callback : coroutine = callback
        self.callback_args : dict = callback_args
        self.ephemeral : bool = ephemeral and not target
        confirmation_button = disnake.ui.Button(label = "Confirmer", emoji="✅", style=disnake.ButtonStyle.green)
        confirmation_button.callback = self.validate
        cancel_button = disnake.ui.Button(label = "Annuler", emoji = "❌", style= disnake.ButtonStyle.danger)
        cancel_button.callback = self.cancel

        
        self.add_item(confirmation_button)
        self.add_item(cancel_button)
        
        self.embed = FastEmbed(
            title=title,
            description=message,
            color=color.gris
        )
        
    @staticmethod
    async def confirm(inter : disnake.Interaction, callback : coroutine, callback_args : dict = {}, target : Union[disnake.TextChannel,disnake.User] = None, title : str = "Confirmation", message : str = "Confirmer l'action ?", ephemeral : bool = True, timeout : int = 180):
        newConfirmationView = ConfirmationView(inter,callback, callback_args=callback_args, target=target, title=title, message=message, ephemeral=ephemeral, timeout=timeout)
        await newConfirmationView.send()
        
    async def send(self):
        if self.target:
            await self.inter.response.defer(ephemeral = self.ephemeral)
            await self.target.send(embed=self.embed, view=self)
        else:
            await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=self.ephemeral)
        
    async def cancel(self, interaction : disnake.MessageInteraction):
        self.stop()
        await interaction.response.edit_message(embed=FastEmbed(description="❌ Annulé",color=color.rouge),view=None)
        if not self.ephemeral:
            await interaction.delete_original_message(delay=2)
        
    async def validate(self, interaction : disnake.MessageInteraction):
        self.stop()
        await interaction.response.edit_message(embed=FastEmbed(description="✅ Confirmé",color=color.vert),view=None)
        if self.target:
            await interaction.delete_original_message(delay=2)
            await self.callback(self.callback_args, self.inter)
        else:
            await self.callback(self.callback_args, interaction)
        
    async def on_timeout(self) -> None:     #TODO also delete the targeted msg if target
        if self.ephemeral:
            await self.inter.edit_original_message(embed=FastEmbed(description="⌛ Temps écoulé",color=color.rouge),view=None)
        else:
            await self.inter.delete_original_message()