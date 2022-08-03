from enum import Enum
import disnake


from .Embed import Embed

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
    
    def __init__(self, inter : disnake.Interaction, title : str, message : str, timeout : int, color : disnake.Colour, confirmationLabel : str, cancelLabel : str):
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
        
        self.embed = Embed(
            title=title,
            description=message,
            color=color
        )

        self.state : ConfirmationStatus = ConfirmationStatus(State.UNKOWN)
            
    async def send(self):
        if self.is_application_interaction:
            if self.inter.response.is_done():
                original_embeds = (await self.inter.original_message()).embeds
                await self.inter.edit_original_message(embeds=original_embeds+[self.embed], view=self)
            else:
                await self.inter.response.send_message(embed=self.embed, view=self, ephemeral=True)
        elif self.is_view_interaction:
            original_embeds = self.inter.message.embeds
            await self.inter.response.edit_message(embeds=original_embeds+[self.embed], view=self)


        
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
          
