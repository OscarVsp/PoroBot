# -*- coding: utf-8 -*-
import disnake
from disnake import ApplicationCommandInteraction
from disnake.ext import commands


from .exceptions import *
from .view import *
from .watcher import *
from bot.bot import Bot
from modules.Assets import *

def warning(message: str) -> disnake.Embed:
    return disnake.Embed(title="⚠", description=message, color=disnake.Colour.orange()).set_thumbnail(Images.Poros.SWEAT)


def error(message: str) -> disnake.Embed:
    return disnake.Embed(title=":x:", description=message, color=disnake.Colour.orange()).set_thumbnail(Images.Poros.SHOCKED)


class PoroFeed(disnake.ui.View):
    def __init__(self, inter: ApplicationCommandInteraction):
        super().__init__(timeout=10)
        self.inter = inter
        self.counter = 0

    @disnake.ui.button(
        emoji="<:porosnack:908477364135161877>", label="Donner un porosnack", style=disnake.ButtonStyle.primary
    )
    async def feed(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.counter += 1
        logging.debug(f"PoroFeedView#{self.id} counter is now {self.counter}.")
        if self.counter < 10:
            await interaction.response.edit_message(
                embed=disnake.Embed(
                    description="Continue à nourrir le poro !"
                ).set_image(
                    Images.Poros.POROGROWINGS[self.counter]
                ).set_footer(
                    text=f"{self.counter}/10"
                ),
                view=self,
            )
        else:
            logging.debug(f"PoroFeedView#{self.id} is at max ({self.counter}).")
            self.remove_item(button)
            await interaction.response.edit_message(
                embed=disnake.Embed(description="*#Explosion de poros*").set_image(Images.Poros.POROGROWINGS[self.counter]),
                view=self,
            )

    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()
        logging.debug(f"PoroFeedView#{self.id} timeout")

class Lol(commands.Cog):
    
    def __init__(self, bot):
        """Initialize a Lol cog object and laod the lore of the members.

        Get the member dict for the lore from the "Members.json" file next to it.
        """
        self.bot: Bot = bot
        
    @commands.slash_command(description="Nourrir le poro avec des porosnacks jusqu'à le faire exploser")
    async def porosnack(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=disnake.Embed(description="Nourris le poro !").set_image(Images.Poros.POROGROWINGS[0]).set_footer(text="0/10"),
            view=PoroFeed(inter),
        )

    @commands.slash_command(name="live", description="Info sur une partie en cours")
    async def live(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(
            description="Le nom de l'invocateur à rechercher. Peut être vide pour soit-même si tu as lié ton compte",
        ),
    ):
        await inter.response.defer(ephemeral=True)
        view = CurrentGameView(invocateur)
        await view.start(inter)

    @commands.slash_command(name="invocateur", description="Info sur un invocateur")
    async def invocateur(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(description="Le nom de l'invocateur."),
    ):
        await inter.response.defer(ephemeral=False)
        try:
            summoner = await Summoner(name=invocateur).get()
            await inter.edit_original_message(embed=await summoner.embed)
        except NotFound:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur..."
                ).set_footer(
                    text="Tu peux rejeter ce message pour le faire disparaitre"
                ),
                view=None,
            )
            await inter.delete_original_message(delay=3)

    @commands.slash_command(name="masteries", description="Info sur les masteries d'un invocateur")
    async def masteries(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(description="Le nom de l'invocateur."),
    ):
        await inter.response.defer(ephemeral=True)
        try:
            summoner = await Summoner(name=invocateur).get()
            masteries = await summoner.champion_masteries.get()
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Envoie en privé",
                    description=f"La list des maitrises va t'être envoyé en privé."
                ).set_footer(
                    text="Tu peux rejeter ce message pour le faire disparaitre"
                ),
                view=None,
            )
            embeds = await masteries.embeds
            i = 0
            while len(embeds) > 10 * (i + 1):
                await inter.author.send(embeds=embeds[10 * i : 10 * (i + 1)])
                i += 1
            await inter.author.send(embeds=embeds[10 * i :])
        except NotFound:
            await inter.edit_original_message(
                embed=disnake.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur..."
                ).set_footer(
                    text="Tu peux rejeter ce message pour le faire disparaitre"
                ),
                view=None,
            )
            await inter.delete_original_message(delay=3)

    @commands.slash_command(name="clash", description="Scouter une team clash à partir du nom d'un des joueurs")
    async def clash(
        self,
        inter: ApplicationCommandInteraction,
        summoner: str = commands.Param(description="Le nom d'invocateur d'un des joueurs"),
    ):
        await inter.response.defer(ephemeral=False)
        clashView: ClashTeamView = await ClashTeamView(summoner).get(inter)
        if clashView:
            await clashView.start(inter)

    @commands.slash_command(name="champion", description="Info sur un champion")
    async def champion(
        self, inter: ApplicationCommandInteraction, nom: str = commands.Param(description="Le nom du champion.")
    ):
        await inter.response.defer(ephemeral=True)
        if nom in (await champion_keys_cache.data)["name_by_id"].values():
            championView = await ChampionView(nom).get()
            await championView.start(inter)
        else:
            await inter.edit_original_message(embed=warning(f"Not champion with name **{nom}**"))

    @champion.autocomplete("nom")   #TODO difflib to find closed match (cf. draft)
    async def autocomp_championt(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        champions = []
        for champion in (await champion_keys_cache.data)["name_by_id"].values():
            if champion.lower().startswith(user_input.lower()):
                champions.append(champion)
        if len(champions) > 25:
            champions = champions[:25]
        return champions

    @commands.slash_command(description="Voir combien de temps et d'argent tu as dépensés sur LOL")
    async def wasteonlol(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=disnake.Embed(
                title="__**Wasted on Lol**__",
                description="Utilise les liens ci-dessous pour découvrir combien de temps et/ou d'argent tu as dépensés dans League of Legends"
            ).set_thumbnail(
                Images.Poros.NEUTRAL
            ),
            components=[
                disnake.ui.Button(
                    label="Temps passé sur lol", emoji="⌛", style=disnake.ButtonStyle.link, url="https://wol.gg/"
                ),
                disnake.ui.Button(
                    label="Argent dépensé sur lol",
                    emoji="💰",
                    style=disnake.ButtonStyle.link,
                    url="https://support-leagueoflegends.riotgames.com/hc/fr/articles/360026080634",
                ),
            ],
            delete_after=60,
        )

    @commands.slash_command(description="Obtenir les règles de l'aram à boire")
    async def drink(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(embed=drink_embed)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Lol(bot))
