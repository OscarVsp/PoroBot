# -*- coding: utf-8 -*-
from typing import List

import disnake

import modules.FastSnake as FS


class PollCreationView(disnake.ui.View):
    def __init__(self, inter: disnake.ApplicationCommandInteraction, title: str, role: disnake.Role = None):
        super().__init__(timeout=None)
        self.inter = inter
        self.title: str = title
        self.role: disnake.Role = role
        self.description: str = None
        self.options: List[str] = []
        self.send.disabled = True

    @property
    def embed(self) -> disnake.Embed:
        embed = FS.Embed(
            title="**__Création du sondage__**",
        )

        embed.add_field(
            name="**Mention**", value=self.role.mention if self.role else "*Pas de role à mentionner*", inline=False
        )
        embed.add_field(name="**Titre**", value=f"> {self.title}", inline=False)
        embed.add_field(
            name="**Description**",
            value=f"> {self.description }" if self.description else "*Pas de description*",
            inline=False,
        )
        embed.add_field(
            name="**Options**",
            value="\n".join([f"{FS.Emotes.ALPHA[i]} {option}" for i, option in enumerate(self.options)])
            if self.options
            else "*Ajouter au moins une options*",
            inline=False,
        )
        return embed

    async def update(self, inter: disnake.MessageInteraction = None):
        self.send.disabled = len(self.options) == 0
        if inter:
            if inter.response.is_done():
                await inter.edit_original_message(embed=self.embed, view=self)
            else:
                await inter.response.edit_message(embed=self.embed, view=self)
        else:
            await self.inter.edit_original_message(embed=self.embed, view=self)

    @disnake.ui.button(label="set description", row=1)
    async def set_description(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(PollDescriptionModal(self))

    @disnake.ui.button(label="clear description", row=1)
    async def clear_description(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.description = None
        await self.update(interaction)

    @disnake.ui.button(label="Add option", row=2)
    async def add_option(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.send_modal(PollOptionModal(self))

    @disnake.ui.button(label="clear options", row=2)
    async def clear_option(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.options = []
        await self.update(interaction)

    @disnake.ui.button(label="Send", row=3)
    async def send(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()
        self.stop()
        embed = disnake.Embed(
            title=self.title,
            description=self.description if self.description else disnake.Embed.Empty,
            color=disnake.Colour.purple(),
        )
        embed.add_field(
            name="**Options**",
            value="\n".join([f"{FS.Emotes.ALPHA[i]} {option}" for i, option in enumerate(self.options)]),
        )
        pollMsg = await self.inter.channel.send(content=self.role.mention if self.role else None, embed=embed)
        [await pollMsg.add_reaction(FS.Emotes.ALPHA[i]) for i in range(len(self.options))]
        await interaction.response.edit_message(embed=disnake.Embed(description="Sondage envoyée !"), view=None)

    @disnake.ui.button(label="cancel", row=3)
    async def cancel(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.stop()
        await interaction.response.edit_message(embed=disnake.Embed(description="Sondage annulé..."), view=None)


class PollOptionModal(disnake.ui.Modal):
    def __init__(self, sondage: "PollCreationView") -> None:
        self.sondage: "PollCreationView" = sondage
        super().__init__(
            title="Création d'une option", components=[disnake.ui.TextInput(label="Nom de l'option", custom_id="name")]
        )

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        await interaction.response.defer()
        self.sondage.options.append(interaction.text_values.get("name"))
        await self.sondage.update()
        await interaction.delete_original_message()


class PollDescriptionModal(disnake.ui.Modal):
    def __init__(self, sondage: "PollCreationView") -> None:
        self.sondage: "PollCreationView" = sondage
        super().__init__(
            title="Ajout d'une description",
            components=[
                disnake.ui.TextInput(
                    label="Description", custom_id="description", style=disnake.TextInputStyle.paragraph
                )
            ],
        )

    async def callback(self, interaction: disnake.ModalInteraction, /) -> None:
        await interaction.response.defer()
        self.sondage.description = interaction.text_values.get("description")
        await self.sondage.update()
        await interaction.delete_original_message()
