# -*- coding: utf-8 -*-
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

import disnake

from modules.FastSnake.ConfirmationView import ConfirmationReturnData
from modules.FastSnake.ConfirmationView import ConfirmationView
from modules.FastSnake.ConfirmationView import Target


class ButtonChoice:
    def __init__(self, label: str, emoji: Optional[Union[str, disnake.PartialEmoji]] = None):
        self.label: str = label
        self.emoji: Optional[Union[str, disnake.PartialEmoji]] = emoji

    def to_button(
        self, row: int = None, style: disnake.ButtonStyle = disnake.ButtonStyle.secondary
    ) -> disnake.ui.Button:
        return disnake.ui.Button(label=self.label, emoji=self.emoji, style=style, row=row)

    @staticmethod
    def from_button(button: disnake.ui.Button):
        return ButtonChoice(label=button.label, emoji=button.emoji)

    def __eq__(self, __o: object) -> bool:
        if isinstance(__o, disnake.Button):
            return self.label == __o.label
        elif isinstance(__o, ButtonChoice):
            return self.label == __o.label
        return False


class QCMView(ConfirmationView):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        color: disnake.Colour,
        choices: List[ButtonChoice],
        pre_selection: ButtonChoice,
    ):
        super().__init__(target, embeds, title, description, timeout, color)

        if len(choices) > 20:
            raise ValueError("Size of choices should be at max 20")

        for i, choice in enumerate(choices):
            choice_button = choice.to_button(row=(1 + i // 5))
            choice_button.callback = self.call_back
            self.add_item(choice_button)

        self.response: ButtonChoice = pre_selection
        self.confirm.disabled = not (self.response)

    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.response:
            embed.add_field(
                name="__**Choix actuel**__",
                value=f"> {self.response.emoji if self.response.emoji else '◾'} **{self.response.label}**",
            )
        embed.set_footer(text="Un seul choix possible.")
        return embed

    async def call_back(self, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.response = ButtonChoice.from_button(interaction.component)
        self.confirm.disabled = False
        await self.update(interaction)


class QCMReturnData(ConfirmationReturnData):
    def __init__(self, qcmView: QCMView):
        super().__init__(qcmView)
        if self.is_confirmed:
            self._response = qcmView.response
        else:
            self._response = None

    @property
    def response(self) -> Optional[ButtonChoice]:
        return self._response

    @property
    def label(self) -> Optional[str]:
        if self._response:
            return self._response.label

    @property
    def emoji(self) -> Optional[disnake.PartialEmoji]:
        if self._response:
            return self._response.emoji


class QRMView(ConfirmationView):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        color: disnake.Colour,
        choices: List[ButtonChoice],
        pre_selection: List[ButtonChoice],
        min: int,
        max: Optional[int],
    ):
        super().__init__(target, embeds, title, description, timeout, color)
        if len(choices) > 20:
            raise ValueError("Size of choices should be at max 20")

        self.min: int = min
        self.max: int = max if max else len(choices)

        if self.min == self.max:
            self.footer = f"Exactement {self.min} réponses nécessaires."
        elif self.min == 0:
            if self.max == len(choices):
                self.footer = f"Pas de limite de nombre de réponses."
            else:
                self.footer = f"Au maximum {self.max} réponses possibles."
        else:
            if self.max == len(choices):
                self.footer = f"Au minimun {self.min} réponses nécessaire."
            else:
                self.footer = f"Entre {self.min} et {self.max} réponses possibles."

        for i, choice in enumerate(choices):
            choice_button = choice.to_button(row=(1 + i // 5))
            choice_button.callback = self.call_back
            self.add_item(choice_button)

        self.responses: List[ButtonChoice] = pre_selection.copy() if pre_selection else []
        self.check_validity()

    def check_validity(self) -> None:
        if len(self.responses) < self.min:
            self.confirm.disabled = True
            self.confirm.label = "Pas assez de réponse"
        elif len(self.responses) > self.max:
            self.confirm.disabled = True
            self.confirm.label = "Trop de réponse"
        else:
            self.confirm.disabled = False
            self.confirm.label = "Confirmer"

    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.responses != []:
            embed.add_field(
                name="__**Choix actuel**__",
                value="\n".join(f"> {r.emoji if r.emoji else '◾'} **{r.label}**" for r in self.responses),
            )
        embed.set_footer(text=self.footer)
        return embed

    async def call_back(self, interaction: disnake.MessageInteraction):
        choice = interaction.component
        if choice in self.responses:
            self.responses.remove(choice)
        else:
            self.responses.append(ButtonChoice.from_button(choice))
        self.check_validity()
        await self.update(interaction)


class QRMReturnData(ConfirmationReturnData):
    def __init__(self, qRmView: QRMView):
        super().__init__(qRmView)
        if self.is_confirmed:
            self._responses = qRmView.responses
        else:
            self._responses = []

    @property
    def responses(self) -> List[ButtonChoice]:
        return self._responses

    @property
    def labels(self) -> List[str]:
        return [r.label for r in self._responses]

    @property
    def emojis(self) -> List[Optional[disnake.PartialEmoji]]:
        return [r.emoji for r in self._responses]


class SelectionRow:
    def __init__(
        self,
        label: str,
        options: List[Union[str, Tuple[str, str]]],
        min_values: int = 1,
        max_values: int = None,
        defaults: Union[str, List[str]] = None,
    ):
        self.label: str = label
        self.options: List[Union[str, Tuple[str, str]]] = options
        self.min_values: int = min_values
        self.max_values: int = max_values if max_values else len(self.options)

    def to_components(self, row: int) -> disnake.ui.Select:
        return disnake.ui.Select(
            placeholder=self.label,
            min_values=self.min_values,
            max_values=self.max_values,
            row=row,
            options=[
                (disnake.SelectOption(label=option))
                if isinstance(option, str)
                else disnake.SelectOption(label=option[0], emoji=option[1])
                for option in self.options
            ],
        )


class SelectionView(ConfirmationView):
    def __init__(
        self,
        target: Target,
        embeds: List[disnake.Embed],
        title: str,
        description: str,
        timeout: int,
        options: List[SelectionRow],
        color: disnake.Colour = disnake.Colour.default(),
        thumbnail: str = None,
    ):
        super().__init__(target, embeds, title, description, timeout, color, thumbnail)
        if isinstance(options, SelectionRow):
            self.options: List[SelectionRow] = [options]
        else:
            self.options: List[SelectionRow] = options

        if len(self.options) > 3:
            raise ValueError("Number of selection row should be lower or equal to 3.")

        for selection_row in self.options:
            if len(selection_row.options) > 25:
                raise ValueError("Number of options in one row should be lower or equal to 25")

        self.selection_rows: List[disnake.ui.Select] = []
        self.labels = [option.label for option in options]

        for i, selection_row in enumerate(self.options):
            new_selection_row = selection_row.to_components(i + 1)
            new_selection_row.callback = self.call_back
            self.selection_rows.append(new_selection_row)
            self.add_item(new_selection_row)
        self.check_validity()

    def check_validity(self) -> None:
        disabled: bool = False
        for row in self.selection_rows:
            row.placeholder = ", ".join([value for value in row.values])
            if len(row.values) < row.min_values or len(row.values) > row.max_values:
                disabled = True
                break
        self.confirm.disabled = disabled

    @property
    def embed(self) -> disnake.Embed:
        embed = super().embed
        if self.selection_rows != []:
            for j, row in enumerate(self.selection_rows):
                embed.add_field(
                    name=f"__**{self.labels[j]}**__",
                    value=("\n".join(f"> **{value}**" for value in row.values) if row.values != [] else "*N/A*"),
                    inline=False,
                )
        return embed

    async def call_back(self, interaction: disnake.MessageInteraction):
        self.check_validity()
        await self.update(interaction)


class SelectionViewReturnData(ConfirmationReturnData):
    def __init__(self, selectionView: SelectionView):
        super().__init__(selectionView)
        if self.is_confirmed:
            self._responses = [selection.values for selection in selectionView.selection_rows]
        else:
            self._responses = []

    @property
    def responses(self) -> List[ButtonChoice]:
        return self._responses
