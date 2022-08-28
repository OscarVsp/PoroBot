# -*- coding: utf-8 -*-
from typing import List

import disnake

import modules.FastSnake as FS
from .watcher import *
from modules.LolPatchNoteScraper import PatchNote

drink_embed = FS.Embed(
    title="__**:underage: RÈGLES DE L'ARAM À BOIRE ! :beers:**__",
    description="""✅ :arrow_right: Donner une gorgée :beers:
                         :o2: :arrow_right: Boire une gorgée :beers:
                         :vs: :arrow_right: ✅ ou :o2: en fonction.""",
    fields=[
        {
            "name": "__Pendant la partie :__",
            "value": """> 1️⃣ Faire un kill ...................................................... ✅1️⃣
                             > :two: Mourrir ............................................................. :o2:1️⃣
                             > :three: Toutes les 5 assist ......................................... ✅1️⃣
                             > :four: First blood ........................................................ :vs:1️⃣
                             > :five: Pentakill ............................................................ :vs::five:
                             > :six: Faire un kill dans la fontaine (et survivre) ✅:two: (:four:)
                             > :seven: Toucher le nexus ............................................ :o2:1️⃣
                             > :eight: Dans la fontaine sur l'écran de victoire .... ✅:three:""",
        },
        {
            "name": "__Après la partie :__",
            "value": """> 1️⃣ Perfect game (0 mort) ................................. ✅:five:
                             > :two: 100% kill participation ................................. ✅:five:
                             > :three: Perfect support (0 kill) ................................ ✅:three:
                             > :four: Abandon .......................................................... :o2::five:
                             > :five: Avoir tilt ........................................................... :o2::five:""",
        },
        {
            "name": "__Spectateur :__",
            "value": """> S'il y a un spectateur,celui-ci doit choisir un joueur avant la partie. Chaque fois que ce joueur doit ✅ ou :o2:, le spectateur fait de même.
                             > Celui-ci peut donner des gorgées à n'importe quel joueur et n'importe quel joueur pour lui donner des gorgées.""",
        },
    ],
    thumbnail=FS.Images.Poros.GRAGAS,
)


class PatchNoteView(disnake.ui.View):
    def __init__(self, inter: disnake.ApplicationCommandInteraction, previous: int = 0, lang: str = None):
        super().__init__(timeout=60 * 10)
        self.inter: disnake.ApplicationCommandInteraction = inter

        if lang != None and lang in PatchNote.langs:
            self.patch: PatchNote = PatchNote(previous=previous, lang=lang)
        elif inter.locale == disnake.Locale.fr:
            self.patch: PatchNote = PatchNote(previous=previous, lang="fr-fr")
        else:
            self.patch: PatchNote = PatchNote(previous=previous, lang="en-gb")

        self.embed: disnake.Embed = FS.Embed(
            author_name=f"Patch {self.patch.season_number}.{self.patch.patch_number}",
            title=f"{self.patch.title}",
            description=self.patch.description,
            url=self.patch.link,
            image=self.patch.overview_image,
            thumbnail=FS.Images.Lol.LOGO,
            color=disnake.Colour.dark_blue(),
        )
        self.add_item(
            disnake.ui.Button(
                style=disnake.ButtonStyle.link,
                url=self.patch.link,
                label=f"Patch {self.patch.season_number}.{self.patch.patch_number}",
                emoji="<:Lol:658237632786071593>",
            )
        )

    async def on_timeout(self) -> None:
        await self.inter.delete_original_message()


class CurrentGameView(disnake.ui.View):
    def __init__(self, summoner_name: str):
        super().__init__(timeout=60 * 60)
        self.summoner_name: str = summoner_name
        self.live_game: CurrentGame = None
        self.embeds_cached: List[List[disnake.Embed]] = None
        self.current_participant_index: Tuple[int, int] = None
        self.inter: disnake.MessageCommandInteraction = None
        self.gameEmbed: disnake.Embed = None
        self.teamEmbeds: List[disnake.Embed] = None

    async def start(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
        try:
            summoner = await Summoner(name=self.summoner_name).get()
        except NotFound:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{self.summoner_name}*** ne correspond à aucun invocateur...",
                ),
                view=None,
            )
            await inter.delete_original_message(delay=3)
            return

        await inter.edit_original_message(
            embeds=[await summoner.embed, FS.Embed(description=f"{FS.Emotes.LOADING} *Recherche de game en cours...*")]
        )
        try:
            self.live_game = await CurrentGame(summoner_id=summoner.id).get()
        except NotFound:
            await inter.edit_original_message(
                embeds=[(await summoner.embed), FS.Embed(description="*Pas de partie en cours*")]
            )
            await inter.delete_original_message(delay=10)
            return

        await inter.edit_original_message(
            embeds=[await summoner.embed, FS.Embed(description=f"{FS.Emotes.LOADING} *Récupération des données...*")]
        )

        self.buttons: List[disnake.ui.Button] = []
        self.embeds_cached = []
        for i, team in enumerate(self.live_game.teams):
            self.embeds_cached.append([])
            for j, participant in enumerate(team.participants):
                self.embeds_cached[i].append(None)
                name = participant.summoner_name
                if len(name) > 7:
                    name = name[:7]
                button = disnake.ui.Button(
                    custom_id=f"{i}:{j}",
                    emoji=(await MerakiChampion(id=participant.champion_id).get()).emote,
                )
                button.callback = self.call_back
                self.add_item(button)
                self.buttons.append(button)
                if participant.summoner_name == summoner.name:
                    self.current_participant_index = (i, j)
        await self.update(inter)

    async def embeds(self) -> List[disnake.Embed]:
        if self.embeds_cached[self.current_participant_index[0]][self.current_participant_index[1]] == None:
            self.embeds_cached[self.current_participant_index[0]][
                self.current_participant_index[1]
            ] = await self.live_game.participant_embed(
                self.live_game.teams[self.current_participant_index[0]].participants[self.current_participant_index[1]]
            )
        if self.gameEmbed == None:
            self.gameEmbed = self.live_game.configEmbed
            for field in await self.live_game.team_fields:
                self.gameEmbed.add_field(name=field.get("name"), value=field.get("value"))
        return [
            self.embeds_cached[self.current_participant_index[0]][self.current_participant_index[1]],
            self.gameEmbed,
        ]

    async def update(self, inter: disnake.MessageInteraction):
        for button in self.buttons:
            button.disabled = [int(i) for i in button.custom_id.split(":")] == self.current_participant_index
        if inter.response.is_done():
            await inter.edit_original_message(embeds=await self.embeds(), view=self)
        else:
            await inter.response.edit_message(embeds=await self.embeds(), view=self)

    async def call_back(self, inter: disnake.MessageInteraction):
        await inter.response.defer()
        self.current_participant_index = [int(i) for i in inter.component.custom_id.split(":")]
        await self.update(inter)


class ClashTeamView(disnake.ui.View):
    def __init__(self, summoner_name: str):
        super().__init__(timeout=60 * 60)
        self.summoner_name: str = summoner_name
        self.current_summoner: Summoner = None
        self.team: ClashTeam = None
        self.summoners: List[Summoner] = None
        self.inter: disnake.MessageCommandInteraction = None

    async def get(self, inter: disnake.ApplicationCommandInteraction) -> Optional["ClashTeamView"]:
        try:
            summoner = await Summoner(name=self.summoner_name).get()
            clashPlayers = await summoner.clash_players.get()
            if len(clashPlayers.players) > 0:
                self.team = ClashTeam(id=clashPlayers.players[0].team_id)
                self.summoners: List[Summoner] = [await player.summoner.get() for player in self.team.players]
                return self
            else:
                await inter.edit_original_message(
                    embed=FS.Embed(
                        title="Pas de team clash",
                        description=f"L'invocateur ***{self.summoner_name}*** ne fais pas parti d'une équipe clash...",
                    ),
                    view=None,
                )
                await inter.delete_original_message(delay=5)
                return None
        except NotFound:
            await inter.edit_original_message(
                embed=FS.Embed(
                    title="Invocateur inconnu",
                    description=f"Le nom d'invocateur ***{self.summoner_name}*** ne correspond à aucun invocateur...",
                ),
                view=None,
            )
            await inter.delete_original_message(delay=5)
            return None

    async def start(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
        self.buttons: List[disnake.ui.Button] = []
        for i in range(len(self.summoners)):
            name = self.summoners[i].name
            if len(name) > 12:
                name = name[:12]
            button = disnake.ui.Button(
                label=name, custom_id=f"{i}", emoji=FS.Emotes.Lol.Positions.get(self.team.players[i].position)
            )
            button.callback = self.call_back
            self.add_item(button)
            self.buttons.append(button)
            if self.summoners[i].name.lower() == self.summoner_name.lower():
                self.current_summoner = self.summoners[i]
        self.add_item(
            disnake.ui.Button(
                style=disnake.ButtonStyle.link, url=await self.team.opgg_url(), emoji=FS.Emotes.Lol.OPGG, row=2
            )
        )
        await self.update(inter)

    @async_property
    async def embeds(self) -> List[disnake.Embed]:
        return [await self.current_summoner.embed, await self.team.embed]

    async def update(self, inter: disnake.MessageInteraction):
        for button in self.buttons:
            button.disabled = self.current_summoner.name.lower().startswith(button.label.lower())
        if inter.response.is_done():
            await inter.edit_original_message(embeds=await self.embeds, view=self)
        else:
            await inter.response.edit_message(embeds=await self.embeds, view=self)

    async def call_back(self, inter: disnake.MessageInteraction):
        self.current_player = next(
            (s for s in self.summoners if s.name.lower().startswith(inter.component.label.lower())), None
        )
        await self.update(inter)


class ChampionView(disnake.ui.View):
    def __init__(self, champion_name: str):
        super().__init__(timeout=60 * 60)
        self.champion_name: str = champion_name
        self.champion: MerakiChampion = None
        self.embeds: disnake.Embed = None
        self.inter: disnake.MessageCommandInteraction = None

    async def get(self) -> Optional["ChampionView"]:
        self.champion = await MerakiChampion(name=self.champion_name).get()
        self.embeds = self.champion.embeds
        return self

    async def start(self, inter: disnake.ApplicationCommandInteraction):
        self.inter = inter
        self.overview.disabled = True
        await self.update(inter)

    async def update(self, inter: disnake.MessageInteraction):
        if inter.response.is_done():
            await inter.edit_original_message(embeds=self.embeds, view=self)
        else:
            await inter.response.edit_message(embeds=self.embeds, view=self)

    @disnake.ui.button(label="Overview", row=1)
    async def overview(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.embeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="Advanced stats", row=1)
    async def advanced(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.advanced_stats
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="P", row=2)
    async def passive(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.Pembeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="Q", row=2)
    async def QSpell(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.Qembeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="W", row=2)
    async def WSpell(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.Wembeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="E", row=2)
    async def ESpell(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.Eembeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)

    @disnake.ui.button(label="R", row=2)
    async def RSpell(self, button: disnake.ui.Button, inter: disnake.MessageInteraction):
        self.embeds = self.champion.Rembeds
        for other_button in self.children:
            other_button.disabled = False
        button.disabled = True
        await self.update(inter)
