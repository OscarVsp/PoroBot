# -*- coding: utf-8 -*-
from typing import List

import disnake

import modules.FastSnake as FS
from .scraper import Almanax_scraper


class AlmanaxView(disnake.ui.View):

    MONTHS = {
        "01": "janvier",
        "02": "février",
        "03": "mars",
        "04": "avril",
        "05": "mai",
        "06": "juin",
        "07": "juillet",
        "08": "août",
        "09": "septembre",
        "10": "octobre",
        "11": "novembre",
        "12": "décembre",
    }

    def __init__(self):
        super().__init__(timeout=None)

    @disnake.ui.button(emoji=":calendar_spiral:", label="Semaine", style=disnake.ButtonStyle.primary)
    async def week(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed=self.data_to_embed(Almanax_scraper.get_almanax(7)))

    @disnake.ui.button(emoji=":calendar_spiral:", label="Mois", style=disnake.ButtonStyle.primary)
    async def month(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed=self.data_to_embed(Almanax_scraper.get_almanax(31)))

    @disnake.ui.button(emoji=":calendar_spiral:", label="Année", style=disnake.ButtonStyle.primary)
    async def year(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.author.send(embed=self.data_to_embed(Almanax_scraper.get_almanax(365)))

    @classmethod
    def data_to_embed(cls, data) -> List[disnake.Embed]:
        if type(data) == list:
            max_embed_size = 4000
            embeds: List[disnake.Embed] = [
                disnake.Embed(
                    title=f":calendar_spiral: __**Almanax des {len(data)} prochains jours**__ :calendar_spiral:"
                )
            ]
            offrandes: List[str] = [f"{d['date']} : **{d['item_quantity']}x** {d['item']}" for d in data]
            text: str = ""
            for offrand in offrandes:
                if len(text) + len(offrand) > max_embed_size:
                    embeds.append(disnake.Embed(description=text))
                    text = ""
                text += offrand + "\n"
            embeds.append(disnake.Embed(description=text))
            return embeds

        return [
            FS.Embed(
                title=f":calendar_spiral: __**Almanax du {data['date']}**__ :calendar_spiral:",
                fields=[
                    {"name": "__Offrande :__", "value": f"**{data['item_quantity']}x** {data['item']}"},
                    {"name": "__Bonus :__", "value": f"{data['description']}"},
                ],
                thumbnail=f"{data['item_picture_url']}",
            )
        ]
