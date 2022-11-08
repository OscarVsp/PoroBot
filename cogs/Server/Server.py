# -*- coding: utf-8 -*-
import disnake
from deep_translator import GoogleTranslator
from disnake.ext import commands

from .view import PollCreationView
from bot.bot import Bot


class Server(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: Bot = bot
        self.translator = GoogleTranslator(source="auto", target="en")
        self.registration_role = None

    def tr(self, text: str) -> str:
        if text != None and text != None:
            return_text = ""
            i = (0, 4999)
            while i[1] < len(text):
                tr_text = self.translator.translate(text[i[0] : i[1]])
                if tr_text:
                    return_text += tr_text
                else:
                    return_text += text[i[0] : i[1]]
                i[0] += 5000
                i[1] += 5000
            tr_text = self.translator.translate(text[i[0] :])
            if tr_text:
                return_text += tr_text
            else:
                return_text += text[i[0] :]
            return return_text
        else:
            return ""

    @commands.message_command(name="Translate")
    async def translate(self, inter: disnake.ApplicationCommandInteraction):
        await inter.response.defer(ephemeral=True)
        content = self.tr(inter.target.content)
        embeds = []
        if inter.target.embeds:
            for embed in inter.target.embeds:
                if embed.title != None:
                    embed.title = self.tr(embed.title)
                if embed.description != None:
                    embed.description = self.tr(embed.description)
                if embed.footer.text:
                    embed.set_footer(text=self.tr(embed.footer.text), icon_url=embed.footer.icon_url)
                if embed.author.name:
                    embed.set_author(
                        name=self.tr(embed.author.name), url=embed.author.url, icon_url=embed.author.icon_url
                    )
                fields = embed.fields.copy()
                embed.clear_fields()
                for field in fields:
                    embed.add_field(name=self.tr(field.name), value=self.tr(field.value), inline=field.inline)

                embeds.append(embed)
        await inter.edit_original_message(
            content=content,
            embeds=embeds,
        )

    @commands.slash_command(name="poll", description="Créer un sondage dans le channel actuel")
    async def poll(
        self,
        inter: disnake.ApplicationCommandInteraction,
        titre: str = commands.Param(description="Le titre du sondage"),
        role: disnake.Role = commands.Param(description="Le role à mentionner", default=None),
    ):
        await inter.response.defer(ephemeral=True)
        pollCreationView = PollCreationView(inter, titre, role)
        await inter.edit_original_message(embed=pollCreationView.embed, view=pollCreationView)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Server(bot))
