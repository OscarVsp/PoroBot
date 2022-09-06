# -*- coding: utf-8 -*-
from math import ceil
from random import shuffle
from typing import Tuple

import disnake
import pickledb
from disnake import ApplicationCommandInteraction
from disnake.ext import commands

import modules.FastSnake as FS
from .exceptions import *
from .view import *
from .watcher import *
from modules.FastSnake.SimpleModal import SimpleModal
from modules.FastSnake.Views import confirmation
from modules.FastSnake.Views import memberSelection


class Lol(commands.Cog):
    def __init__(self, bot):
        """Initialize a Lol cog object and laod the lore of the members.

        Get the member dict for the lore from the "Members.json" file next to it.
        """
        self.bot: commands.InteractionBot = bot
        self.summoners = pickledb.load("cogs/Lol/summoners.db", False)
        self.live_trackers = pickledb.load("cogs/Lol/trackers.db", False)

    @commands.slash_command(name="lol", dm_permission=True)
    async def lol(self, inter):
        pass

    async def set_summoner(self, inter: disnake.Interaction, target: disnake.User, invocateur: str):
        try:
            summoner = await Summoner(name=invocateur).get()
        except NotFound:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...",
                    footer_text="Tu peux rejeter ce message pour le faire disparaitre",
                ),
                view=None,
            )
            return

        confirm = await confirmation(
            inter,
            embeds=[await summoner.embed],
            title="Valider l'invocateur",
            description=f"Est-ce bien ton compte ?",
        )

        if not confirm:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title="Invocateur refusé.",
                    description="Nom d'invocateur non changé.",
                    footer_text="Tu peux rejeter ce message pour le faire disparaitre",
                ),
                view=None,
            )
            return

        if str(target.id) in self.summoners.getall():
            confirm = await confirmation(
                inter,
                embeds=[await summoner.embed],
                title="Invocateur déjà existant",
                description=("Tu as" if target == inter.author else f"{target.mention} a")
                + f" déjà le nom d'invocateur suivant enregistré : ***{self.summoners.get(str(target.id))}***\n Veux-tu le remplacer ?",
                timeout=120,
            )
            if not confirm:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        title="Invocteur inchangé",
                        description="Nom d'invocateur non changé",
                        footer_text="Tu peux rejeter ce message pour le faire disparaitre",
                    ),
                    view=None,
                )
                return

        self.summoners.set(str(target.id), invocateur)
        self.summoners.dump()
        await inter.edit_original_message(
            embed=FS.Embed(
                title="Invocateur enregistré",
                description=f"L'invocateur ***{invocateur}*** à bien été lié avec "
                + ("ton compte discord !" if inter.author == target else f"le compte discord de {target.mention}"),
                footer_text="Tu peux rejeter ce message pour le faire disparaitre.",
            ),
            view=None,
        )

    @lol.sub_command(description="Lier son compte discord avec son compte League of Legends")
    async def account(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(description="Ton nom d'invocateur sur League of Legends"),
    ):
        await inter.response.defer(ephemeral=True)
        await self.set_summoner(inter, inter.author, invocateur)

    async def modal_callback(self, interaction: disnake.ModalInteraction, answers: dict, callback_datas: dict):
        await self.set_summoner(interaction, callback_datas.get("target"), answers.get("summoner_name"))

    @commands.user_command(name="Nom d'invocateur", default_member_permissions=disnake.Permissions.all())
    async def summoner_set(self, inter: ApplicationCommandInteraction, target: disnake.User):
        await inter.response.send_modal(
            SimpleModal(
                f"Définir le nom d'invocateur de {target.display_name}",
                questions=[disnake.ui.TextInput(label="Nom d'invocateur", custom_id="summoner_name")],
                callback=self.modal_callback,
                callback_datas={"target": target},
            )
        )

    async def get_lol_classement(
        self, members_filter: List[disnake.Member]
    ) -> Tuple[List[disnake.Member], List[Summoner]]:
        members: List[disnake.Member] = []
        summoners: List[Summoner] = []

        for member in members_filter:
            if str(member.id) in self.summoners.getall():
                try:
                    new_summoner = await Summoner(name=self.summoners.get(str(member.id))).get()
                    summoners.append(new_summoner)
                    members.append(member)
                except NotFound:
                    pass

        leagues = [
            (await s.league_entries.get()).sorting_score((await s.league_entries.get()).first) for s in summoners
        ]
        sorted_leagues = sorted(leagues, reverse=True)
        sorted_summoners: List[Summoner] = []
        sorted_members: List[disnake.Member] = []
        for league in sorted_leagues:
            sorted_summoners.append(summoners[leagues.index(league)])
            sorted_members.append(members[leagues.index(league)])

        return (sorted_members, sorted_summoners)

    @lol.sub_command(name="classement", description="Classement League of Legends des members du serveur")
    async def classement(
        self,
        inter: ApplicationCommandInteraction,
        filtre: str = commands.Param(
            description="Filtrer les membres à afficher par un role ou un évenement.", default=None
        ),
    ):
        await inter.response.send_message(
            embed=FS.Embed(
                title=f"{FS.Emotes.Lol.LOGO} __**CLASSEMENT LOL**__",
                description=f"{FS.Emotes.LOADING} Création du classement en cours...",
            ),
            ephemeral=False,
        )

        filtre_members: List[disnake.Member] = None

        if inter.guild:

            if filtre:
                filtre_clean = filtre.split(" ")[1]
                for role in inter.guild.roles:
                    if role.name == filtre_clean:
                        filtre_members = role.members
                        break

                if filtre_members == None:
                    for event in inter.guild.scheduled_events:
                        if event.name == filtre_clean:
                            filtre_members = [member async for member in event.fetch_users()]
                            break

            if filtre_members == None or filtre == None:
                filtre_members = inter.guild.members
        else:
            filtre_members = []
            for guild in self.bot.guilds:
                for member in guild.members:
                    if member not in filtre_members:
                        filtre_members.append(member)

        (sorted_members, sorted_summoners) = await self.get_lol_classement(filtre_members)

        ranks = ""
        players = ""

        for i in range(len(sorted_members)):
            entries = await sorted_summoners[i].league_entries.get()
            if entries.first:
                ranks += f"{FS.Emotes.Lol.Tier.get(entries.first.tier)}{FS.Emotes.Lol.Rank.get(entries.first.rank)}\n"
            else:
                ranks += f"{FS.Emotes.Lol.Tier.NONE}{FS.Emotes.Lol.Rank.NONE}\n"
            players += f"**{sorted_members[i].display_name}** (`{sorted_summoners[i].name}`)\n"

        await inter.edit_original_message(
            embed=FS.Embed(
                title=f"{FS.Emotes.Lol.LOGO} __**CLASSEMENT LOL**__",
                description=(f"> *Filtre : {filtre}*" if filtre else ""),
                fields=[
                    {"name": "◾", "value": ranks, "inline": True},
                    {"name": "◾◾◾◾◾◾◾◾◾◾", "value": players, "inline": True},
                ],
                footer_text="""Tu n'es pas dans le classement ?\nLie ton compte League of Legends en utilisant "/lol account" !""",
            )
        )

    @classement.autocomplete("filtre")
    def autocomple_filtre(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        if not inter.guild:
            return "Filter can only be used in guild !"
        filtres = []
        for role in inter.guild.roles:
            if role.name.lower().startswith(user_input.lower()):
                filtres.append(f"👥 {role.name}")
        for event in inter.guild.scheduled_events:
            if event.name.lower().startswith(user_input.lower()):
                filtres.append(f"📅 {event.name}")
        if len(filtres) > 25:
            filtres = filtres[:25]
        return filtres

    @lol.sub_command(name="live", description="Info sur une partie en cours")
    async def live(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(
            description="Le nom de l'invocateur à rechercher. Peut être vide pour soit-même si tu as lié ton compte",
            default=None,
        ),
    ):
        await inter.response.defer(ephemeral=False)
        if invocateur == None:
            if str(inter.author.id) in self.summoners.getall():
                invocateur = self.summoners.get(str(inter.author.id))
            else:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        description="""Spécifie un nom d'invocateur ou bien lie ton compte lol en utilisant "/lol account"."""
                    )
                )
                return

        view = CurrentGameView(invocateur)
        await view.start(inter)

    @lol.sub_command(name="invocateur", description="Info sur un invocateur")
    async def invocateur(
        self,
        inter: ApplicationCommandInteraction,
        invocateur: str = commands.Param(description="Le nom de l'invocateur.", default=None),
    ):
        await inter.response.defer(ephemeral=False)
        if invocateur == None:
            if str(inter.author.id) in self.summoners.getall():
                invocateur = self.summoners.get(str(inter.author.id))
            else:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        description="""Spécifie un nom d'invocateur ou bien lie ton compte lol en utilisant "/lol account"."""
                    )
                )
                return

        try:
            summoner = await Summoner(name=invocateur).get()
            await inter.edit_original_message(embed=await summoner.embed)
        except NotFound:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{invocateur}*** ne correspond à aucun invocateur...",
                    footer_text="Tu peux rejeter ce message pour le faire disparaitre",
                ),
                view=None,
            )
            await inter.delete_original_message(delay=3)

    @lol.sub_command(name="champion", description="Info sur un champion")
    async def champion(
        self, inter: ApplicationCommandInteraction, nom: str = commands.Param(description="Le nom du champion.")
    ):
        await inter.response.defer(ephemeral=False)
        if nom in (await champion_keys_cache.data)["name_by_id"].values():
            championView = await ChampionView(nom).get()
            await championView.start(inter)
        else:
            await inter.edit_original_message(embed=FS.warning(f"Not champion with name **{nom}**"))

    @champion.autocomplete("nom")
    async def autocomp_championt(self, inter: disnake.ApplicationCommandInteraction, user_input: str):
        champions = []
        for champion in (await champion_keys_cache.data)["name_by_id"].values():
            if champion.lower().startswith(user_input.lower()):
                champions.append(champion)
        if len(champions) > 25:
            champions = champions[:25]
        return champions

    def seeding_check(self, **kwargs) -> bool:
        return str(kwargs.get("member").id) in self.summoners.getall()

    @lol.sub_command(
        name="seeding", description="Diviser un groupe en sous groupes en utilisant le classement lol comme seeding"
    )
    async def seeding(
        self,
        inter: ApplicationCommandInteraction,
        nombre: int = commands.Param(description="Nombre de sous groupe", gt=1),
    ):
        if isinstance(inter, disnake.PartialMessageable):
            await inter.response.send_message(
                embed=FS.warning('"/lol seeding" command can only be use on server for the moment.')
            )  # TODO add fitler option in DM and fix member selection to allow dm
        await inter.response.defer(ephemeral=True)
        selection = await memberSelection(
            target=inter, description="Compose le groupe de membre à diviser.", check=self.seeding_check
        )
        if selection:
            await inter.edit_original_message(embed=FS.Embed(description="Composition des groupes..."), view=None)
            (sorted_members, sorted_summoners) = await self.get_lol_classement(selection.members)
            groupes: List[List[Tuple[disnake.Member, Summoner]]] = [[] for _ in range(nombre)]
            for i in range(ceil(len(sorted_members) / nombre)):
                tier_groupe: List[Tuple[disnake.Member, Summoner]] = []
                for j in range(nombre):
                    if i * nombre + j < len(sorted_members):
                        tier_groupe.append((sorted_members[i * nombre + j], sorted_summoners[i * nombre + j]))
                    else:
                        tier_groupe.append(None)
                shuffle(tier_groupe)
                for j, player in enumerate(tier_groupe):
                    if player:
                        groupes[j].append(player)

            ranks = ""
            players = ""

            for i in range(len(sorted_members)):
                entries = await sorted_summoners[i].league_entries.get()
                ranks += f"{FS.Emotes.Lol.Tier.get(entries.first.tier)} **{entries.first.rank}**\n"
                players += f"**{sorted_members[i].mention}** (`{sorted_summoners[i].name}`)\n"

            await inter.channel.send(
                embed=FS.Embed(
                    title=f"{FS.Emotes.Lol.LOGO} __**CLASSEMENT LOL**__",
                    fields=[
                        {"name": "◾", "value": ranks, "inline": True},
                        {"name": "◾◾◾◾◾◾◾◾◾◾", "value": players, "inline": True},
                    ]
                    + [
                        {
                            "name": f"**Groupe {FS.Emotes.ALPHA[i]}**",
                            "value": "\n".join([f"> {member[0].mention}" for member in group]),
                        }
                        for i, group in enumerate(groupes)
                    ],
                ),
                view=None,
            )
            role = await confirmation(
                inter, title="Groupes crées", description="Veux-tu créer des roles à partir de ces groupes ?"
            )
            if role:
                for i, group in enumerate(groupes):
                    role = await inter.guild.create_role(name=f"Groupe {chr(ord('A') +i)}")
                    for member in group:
                        await member[0].add_roles(role)
                await inter.edit_original_message(
                    embed=FS.Embed(
                        description="Roles crées !", footer_text="Tu peux rejeter ce message pour le faire disparaitre"
                    ),
                    view=None,
                )
            else:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        description="Groupes crées !",
                        footer_text="Tu peux rejeter ce message pour le faire disparaitre",
                    ),
                    view=None,
                )
        else:
            await inter.edit_original_message(
                embed=FS.Embed(
                    description=":x Annulé", footer_text="Tu peux rejeter ce message pour le faire disparaitre"
                ),
                view=None,
            )

    @lol.sub_command(
        name="tracker", description="Track your lol games and send you details about the game when it start"
    )
    async def tracker(self, inter: ApplicationCommandInteraction, enable: bool):
        await inter.response.defer(ephemeral=True)
        if str(inter.author.id) not in self.summoners.getall():
            await inter.edit_original_message(
                embed=FS.Embed(
                    title=f"**LIVE GAME TRACKER**",
                    description="⚠️ You need to link your League of Legends account to use this command.\n> Use `/lol account`",
                )
            )
            return
        self.live_trackers.set(str(inter.author.id), enable)
        self.live_trackers.dump()
        if enable:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title=f"**LIVE GAME TRACKER**",
                    description="✅ **Tracker enabled !**\n\nI will send you message about your games when they start.\n\n> The discord activity need to be enable:\n> `Settings > Activity Pricvacy > Display current activity`\n\n> You can disable the tracker with `/lol tracker enable:False`",
                )
            )
        else:
            await inter.edit_original_message(
                embed=FS.Embed(title=f"**LIVE GAME TRACKER**", description="✅ **Tracker disabled !**")
            )

    @commands.slash_command(description="Voir combien de temps et d'argent tu as dépensés sur LOL")
    async def wasteonlol(self, inter: ApplicationCommandInteraction):
        await inter.response.send_message(
            embed=FS.Embed(
                title="__**Wasted on Lol**__",
                description="Utilise les liens ci-dessous pour découvrir combien de temps et/ou d'argent tu as dépensés dans League of Legends",
                thumbnail=FS.Images.Poros.NEUTRAL,
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

    async def send_tracker(self, target: disnake.Member):
        await CurrentGameView(self.summoners.get(str(target.id))).start(target, max=5)
        await asyncio.sleep(5)
        self.live_trackers.set(str(target.id), True)
        self.live_trackers.dump()

    @staticmethod
    def check_start_game(before: disnake.Member, after: disnake.Member, game_name: str):
        for activity in after.activities:
            if activity.name == game_name and activity.state and activity.state.lower() in ["in game", "en jeu"]:
                for activity in before.activities:
                    if (
                        activity.name == game_name
                        and activity.state
                        and activity.state.lower() in ["in game", "en jeu"]
                    ):
                        return False
                return True

    @commands.Cog.listener("on_presence_update")
    async def on_presence_update(self, before: disnake.Member, after: disnake.Member):
        if str(after.id) in self.live_trackers.getall() and self.live_trackers.get(str(after.id)):
            if self.check_start_game(before, after, "League of Legends"):
                self.live_trackers.set(str(after.id), False)
                self.live_trackers.dump()
                await self.send_tracker(after)


def setup(bot: commands.InteractionBot):
    bot.add_cog(Lol(bot))
