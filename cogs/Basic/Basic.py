import disnake
from disnake.ext import commands
from disnake import ApplicationCommandInteraction
import modules.FastSnake as FS
from .view import *


class Basic(commands.Cog):
    def __init__(self, bot):
        """Initialize the cog"""
        self.bot: commands.InteractionBot = bot

    @commands.slash_command(description="Commander un bière (test le ping du bot)")
    async def beer(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(
                title="Voilà tes bières",
                description=f":beer:\n Après {round(self.bot.latency,2)} secondes d'attente seulement !",
                color=disnake.Colour.gold(),
            ),
            view=Beer(inter),
        )

    @commands.slash_command(description="Nourrir le poro avec des porosnacks jusqu'à le faire exploser")
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(description="Nourris le poro !", image=FS.Images.Poros.POROGROWINGS[0], footer_text="0/10"),
            view=PoroFeed(inter),
        )

    @commands.user_command(name="Voir le lore")
    async def lore(self, inter: disnake.UserCommandInteraction):
        lore_embed = get_lore_embed(inter.target.name)
        if lore_embed == False:
            await inter.response.send_message(
                embed=FS.Embed(
                    description=f"{inter.target.name} n'a pas encore de lore...\nDemande à Hyksos de l'écrire !",
                    thumbnail=FS.Images.Poros.SWEAT,
                ),
                ephemeral=True,
            )
        else:
            await inter.response.send_message(embed=lore_embed, delete_after=60 * 5)

    @commands.user_command(name="Créer / éditer le lore", default_member_permissions=disnake.Permissions.all())
    async def addlore(self, inter: disnake.UserCommandInteraction):
        if inter.author.id == 187886815666110465 or inter.author == self.bot.owner:
            await inter.response.send_modal(modal=loreModal(self.bot, inter.target))
        else:
            await inter.response.send_message(
                embed=FS.warning("Seul Hyksos peut utiliser cette commande !"), ephemeral=True
            )


def setup(bot: commands.InteractionBot):
    bot.add_cog(Basic(bot))
