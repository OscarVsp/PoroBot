from disnake.ext import commands
from disnake import ApplicationCommandInteraction
from .view import *


class Clicbang(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(description="Démarrer une partie de bang", dm_permission=False)
    async def bang(
        self,
        inter: ApplicationCommandInteraction,
        valeur_max: int = commands.Param(description="La valeur maximal des cartes (6 par défault)", ge=1, default=6),
    ):
        menu = BangMenu(inter)
        await inter.response.send_message(embed=menu.embed, view=menu)
        if not (await menu.wait()) and not menu.cancelled:
            game = BangGame(inter, menu.players, valeur_max)
            await game.start_game(menu.interaction)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Clicbang(bot))
