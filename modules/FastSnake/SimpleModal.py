from typing import List
import disnake


class SimpleModal(disnake.ui.Modal):
    def __init__(self, title, questions: List[disnake.ui.TextInput], callback, callback_datas: dict = {}):
        components = questions
        self.answers: dict = None
        self.call_back = callback
        self.callback_datas = callback_datas
        super().__init__(title=title, components=components, timeout=600)

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        await interaction.response.defer(ephemeral=True)
        await self.call_back(interaction, interaction.text_values, self.callback_datas)
