import disnake
from typing import Union
from .FastEmbed import FastEmbed
from .data import color


    

class ConfirmationView(disnake.ui.View):
    
    def __init__(self, target : Union[disnake.TextChannel,disnake.User], title : str = "Confirmation", message : str = "Confirmer l'action ?", ephemeral : bool = True, timeout : int = 180):
        super().__init__(timeout=timeout)
        self.target : Union[disnake.Interaction, disnake.TextChannel,disnake.User] = target
        self.is_interaction : bool = isinstance(target, disnake.Interaction)
        self.ephemeral : bool = ephemeral and self.is_interaction and not self.target.response.is_done()
        self.message : disnake.Message = None
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
        
        self.is_confirmed : bool = False
            
    async def send(self):
        if self.is_interaction:
            if self.target.response.is_done():
                await self.target.edit_original_message(embed=self.embed, view=self)
            elif self.ephemeral:
                await self.target.response.send_message(embed=self.embed, view=self, ephemeral=self.ephemeral)
            else:
                await self.target.response.send_message(embed=self.embed, view=self, ephemeral=self.ephemeral)
            self.message = await self.target.original_message()
        else:
            self.message = await self.target.send(embed=self.embed, view=self)

        
    async def cancel(self, interaction : disnake.MessageInteraction):
        await interaction.response.edit_message(embed=FastEmbed(description="❌ Annulé",color=color.rouge),view=None)
        if not self.ephemeral:
            await interaction.delete_original_message(delay=2)
        self.stop()
        
        
    async def validate(self, interaction : disnake.MessageInteraction):
        self.is_confirmed = True
        self.stop()
        await interaction.response.edit_message(embed=FastEmbed(description="✅ Confirmé",color=color.vert),view=None)
        if self.target:
            await interaction.delete_original_message(delay=2)

        
    async def on_timeout(self) -> None:
        if self.ephemeral:
            await self.message.edit(embed=FastEmbed(description="⌛ Temps écoulé",color=color.rouge),view=None)
        else:
            await self.message.delete()
            
          
async def confirmation(target : Union[disnake.TextChannel,disnake.User] = None, title : str = "Confirmation", message : str = "Confirmer l'action ?", ephemeral : bool = True, timeout : int = 180):
    confirmationView = ConfirmationView(target=target, title=title, message=message, ephemeral=ephemeral, timeout=timeout)
    await confirmationView.send()
    await confirmationView.wait()
    return confirmationView.is_confirmed