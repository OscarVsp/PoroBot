import asyncio
from typing import List, Union
import disnake

from modules.FastSnake.Assets import Emotes
from .Embed import Embed
from enum import Enum


class ViewState(Enum):
    CANCELLED = 0
    CONFIRMED = 1
    TIMEOUT = 2
    UNKOWN = 3


Target = Union[
    disnake.ApplicationCommandInteraction,
    disnake.TextChannel,
    disnake.Message,
    disnake.MessageInteraction,
    disnake.ModalInteraction,
]


class ConfirmationView(disnake.ui.View):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        color: disnake.Colour = disnake.Colour.default(),
        thumbnail: str = None,
    ):
        super().__init__(timeout=timeout)
        self.target: Target = target
        self.message_to_delete: disnake.Message = None
        self.embeds: List[disnake.Embed] = embeds if embeds else []
        self.title: str = title
        self.description: str = description
        self.thumbnail: str = thumbnail if thumbnail else disnake.Embed.Empty
        self.color: disnake.Colour = color
        self.interaction: disnake.MessageInteraction = None

        self.state: ViewState = ViewState.UNKOWN

    @property
    def embed(self) -> disnake.Embed:
        return Embed(title=self.title, description=self.description, thumbnail=self.thumbnail, color=self.color)

    async def send(self):
        if isinstance(self.target, disnake.ApplicationCommandInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.send_message(embeds=self.embeds + [self.embed], view=self, ephemeral=True)
        elif isinstance(self.target, disnake.MessageInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.edit_message(embeds=self.embeds + [self.embed], view=self)
        elif isinstance(self.target, disnake.ModalInteraction):
            if self.target.response.is_done():
                await self.target.edit_original_message(embeds=self.embeds + [self.embed], view=self)
            else:
                await self.target.response.send_message(embeds=self.embeds + [self.embed], view=self, ephemeral=True)
        elif isinstance(self.target, disnake.TextChannel):
            self.message_to_delete = await self.target.send(embeds=self.embeds + [self.embed], view=self)
        elif isinstance(self.target, disnake.Message):
            self.message_to_delete = await self.target.channel.send(embeds=self.embeds + [self.embed], view=self)
        else:
            raise TypeError(f"Type {type(self.target)} is not supported.")

    async def update(self, inter: disnake.MessageInteraction):
        if inter.response.is_done():
            await inter.edit_original_message(embeds=self.embeds + [self.embed], view=self)
        else:
            await inter.response.edit_message(embeds=self.embeds + [self.embed], view=self)

    async def end(self) -> None:
        self.stop()
        if self.message_to_delete:
            await self.message_to_delete.delete()

    @disnake.ui.button(label="Confirmer", emoji="✅", style=disnake.ButtonStyle.green)
    async def confirm(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CONFIRMED
        self.interaction = interaction
        await self.end()

    @disnake.ui.button(label="Annuler", emoji=Emotes.RESTART, style=disnake.ButtonStyle.danger)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.state = ViewState.CANCELLED
        self.interaction = interaction
        await self.end()

    async def on_timeout(self) -> None:
        self.state = ViewState.TIMEOUT
        await self.end()


class ConfirmationReturnData:
    def __init__(self, confirmationView: ConfirmationView):
        self._state = confirmationView.state
        self._interaction: disnake.MessageInteraction = confirmationView.interaction

    @property
    def interaction(self) -> disnake.MessageInteraction:
        return self._interaction

    @property
    def is_ended(self) -> bool:
        return self._state != ViewState.UNKOWN

    @property
    def is_confirmed(self) -> bool:
        return self._state == ViewState.CONFIRMED

    @property
    def is_cancelled(self) -> bool:
        return self._state == ViewState.CANCELLED

    @property
    def is_timeout(self) -> bool:
        return self._state == ViewState.TIMEOUT

    def __bool__(self) -> bool:
        return self.is_confirmed
