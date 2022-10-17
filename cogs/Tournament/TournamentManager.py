# -*- coding: utf-8 -*-
from typing import List

from .classes import *
from .TournamentView import AdminView
from .TournamentView import DraftManager
from .TournamentView import PlayerSelectionView
from .TournamentView import RoundView


class Tournament(TournamentData):
    def __init__(
        self,
        guild: disnake.Guild,
        name: str,
        type_str: str,
        size: int,
        banner: str = None,
        nb_round: int = None,
        nb_matches_per_round: int = None,
        nb_teams_per_match: int = None,
        nb_players_per_team: int = None,
        scoreSet: ScoreSet = ScoreSet.default(),
        nb_point_to_win_match: int = 2,
    ):
        super().__init__(
            guild,
            name,
            type_str,
            banner if banner else FS.Images.Tournament.CLASHBANNER,
            size,
            nb_round,
            nb_matches_per_round,
            nb_teams_per_match,
            nb_players_per_team,
            scoreSet,
            nb_point_to_win_match,
        )
        self.admin_view: PlayerSelectionView = None

    async def build(self) -> None:
        self.category = await self.guild.create_category(self.name.upper())
        cat_perm_everyone = disnake.PermissionOverwrite()
        cat_perm_everyone.send_messages = False
        cat_perm_everyone.connect = False
        cat_perm_everyone.view_channel = False
        await self.category.set_permissions(self.everyone, overwrite=cat_perm_everyone)
        self.notif_channel = await self.category.create_text_channel(name="🔔 Annonces")
        self.classement_channel = await self.category.create_text_channel(name="🏅 Classement")
        self.rounds_channel = await self.category.create_text_channel(name="📅 Rounds")
        self.rules_channel = await self.category.create_text_channel(name="📜 Règles")
        self.admin_channel = await self.category.create_text_channel(name="🔧 Admin")
        admin_perm = disnake.PermissionOverwrite()
        admin_perm.view_channel = False
        await self.admin_channel.set_permissions(self.everyone, overwrite=admin_perm)
        self.voice_general = await self.category.create_voice_channel(name="🏆 General")
        for i in range(self._nb_matches_per_round):
            self.voice_channels.append([])
            for j in range(self._nb_teams_per_match):
                if self._nb_matches_per_round == 1:
                    name = f"Équipe {j+1}"
                else:
                    name = f"Match {chr(ord('A') + i)} Équipe {j+1}"
                self.voice_channels[i].append(await self.category.create_voice_channel(name=name))

        self.classement_message = await self.classement_channel.send(embed=self.classement_embed)
        self.roundsView = await RoundView(self).start()
        self.rules_message = await self.rules_channel.send(embed=self.rules_embed)
        playerSelectionView = PlayerSelectionView(self)
        self.admin_message = await self.admin_channel.send(embed=playerSelectionView.embed, view=playerSelectionView)
        cat_perm_everyone.view_channel = True
        await self.category.set_permissions(self.everyone, overwrite=cat_perm_everyone)
        text_voice_channel_perm = disnake.PermissionOverwrite()
        text_voice_channel_perm.connect = True
        text_voice_channel_perm.send_messages = True
        await self.voice_general.set_permissions(self.everyone, overwrite=text_voice_channel_perm)
        for match in self.voice_channels:
            for team in match:
                await team.set_permissions(self.everyone, overwrite=text_voice_channel_perm)

    async def set_players(self, members: List[disnake.Member]) -> None:
        await self.admin_message.delete()
        await super().set_players(members)
        self.role: disnake.Role = await self.guild.create_role(name=self.name)
        for player in self._players:
            await player.add_roles(self.role)
        self.generate_round()
        self.admin_view = AdminView(self)
        self.admin_message = await self.admin_channel.send(embeds=self.admin_embeds, view=self.admin_view)
        await self.update()
        text_voice_channel_perm = disnake.PermissionOverwrite()
        text_voice_channel_perm.connect = True
        text_voice_channel_perm.send_messages = True
        for matchChannels in self.voice_channels:
            for teamChannel in matchChannels:
                await teamChannel.set_permissions(self.role, overwrite=text_voice_channel_perm)
            self.draftManagers.append(
                await DraftManager(
                    self, matchChannels, ["⛔ Ban 1", "✅ Pick 1", "⛔ Ban 2", "⛔ Ban 3", "✅ Pick 2"]
                ).start()
            )

    def generate_round(self) -> None:
        pass

    async def update(self) -> None:
        self.classement_message = await self.classement_message.edit(embed=self.classement_embed)
        await self.roundsView.update()
        self.rules_message = await self.rules_message.edit(embed=self.rules_embed)
        self.save_state()

    def set_score(
        self,
        round: Union[Round, int],
        match: Union[Match, int],
        entity: Union[Entity, int],
        value: int = 1,
        index: int = 0,
    ) -> None:
        super().set_score(round, match, entity, value, index)

    def set_scores(
        self, round: Union[Round, int], match: Union[Match, int], entity: Union[Entity, int], values: List[int]
    ) -> None:
        super().set_scores(round, match, entity, values)

    async def send_notif(self, title: str, description: str) -> None:
        self.notif_messages.append(
            await self.notif_channel.send(
                FS.Embed(
                    author_name=f"{self.name.upper()}",
                    author_icon_url=FS.Images.Tournament.TROPHY,
                    title=title,
                    description=description,
                    color=disnake.Colour.blue(),
                )
            )
        )

    async def delete(self, interaction: disnake.MessageInteraction = None) -> None:
        if interaction:
            await interaction.author.send(embeds=self.admin_embeds)
        await self.notif_channel.delete()
        await self.classement_channel.delete()
        await self.rounds_channel.delete()
        await self.rules_channel.delete()
        await self.voice_general.delete()
        for match_voice in self.voice_channels:
            for team_voice in match_voice:
                await team_voice.delete()
        await self.admin_channel.delete()
        await self.category.delete()
        if self.role:
            await self.role.delete()

    async def on_message(self, message: disnake.Message):
        pass


class Tournament2v2Roll(Tournament):

    TYPE = "2v2 Roll"
    KILL_EMOTE = FS.Emotes.CROSSING_SWORD_WHITE
    TURRET_EMOTE = FS.Emotes.Lol.TURRET
    CS_EMOTE = FS.Emotes.Lol.CS

    class Seeding:
        S4: List[List[List[List[int]]]] = [[[[2, 3], [1, 4]]], [[[1, 3], [2, 4]]], [[[1, 2], [3, 4]]]]

        S5: List[List[List[List[int]]]] = [
            [[[4, 5], [2, 3]]],
            [[[1, 3], [2, 4]]],
            [[[1, 5], [3, 4]]],
            [[[2, 5], [1, 4]]],
            [[[1, 2], [3, 5]]],
        ]

        S8: List[List[List[List[int]]]] = [
            [[[3, 4], [7, 8]], [[5, 6], [1, 2]]],
            [[[6, 8], [5, 7]], [[1, 3], [2, 4]]],
            [[[1, 4], [5, 8]], [[6, 7], [2, 3]]],
            [[[4, 8], [2, 6]], [[3, 7], [1, 5]]],
            [[[3, 8], [1, 6]], [[2, 5], [4, 7]]],
            [[[2, 8], [3, 5]], [[4, 6], [1, 7]]],
            [[[1, 8], [2, 7]], [[4, 5], [3, 6]]],
        ]

    def __init__(self, guild: disnake.Guild, size: int, name: str = "2v2 Roll"):

        if size == 4:
            self._seeding: List[List[List[List[int]]]] = Tournament2v2Roll.Seeding.S4
        elif size == 5:
            self._seeding: List[List[List[List[int]]]] = Tournament2v2Roll.Seeding.S5
        elif size == 8:
            self._seeding: List[List[List[List[int]]]] = Tournament2v2Roll.Seeding.S8

        super().__init__(
            guild,
            name,
            self.TYPE,
            size,
            nb_round=len(self._seeding),
            nb_matches_per_round=len(self._seeding[0]),
            nb_teams_per_match=len(self._seeding[0][0]),
            nb_players_per_team=len(self._seeding[0][0][0]),
            scoreSet=ScoreSet(
                [
                    Score(id=1, score_size=3, name="Kill", emoji=self.KILL_EMOTE, weigth=1.001, per_team=2),
                    Score(id=2, score_size=3, name="Turret", emoji=self.TURRET_EMOTE, weigth=1.0, per_team=1),
                    Score(id=3, score_size=3, name="CS", emoji=self.CS_EMOTE, weigth=0.989, per_team=1),
                ]
            ),
            nb_point_to_win_match=2,
        )

    def generate_round(self) -> None:
        if self.players == None:
            raise PlayersNotSetError
        self.shuffle_players()
        self._rounds = []
        for round_idx in range(self._nb_rounds):
            matches = []
            for match_idx in range(self._nb_matches_per_round):
                teams = []
                for team_idx in range(2):
                    teams.append(
                        Team(
                            [
                                self._players[self._seeding[round_idx][match_idx][team_idx][0] - 1],
                                self._players[self._seeding[round_idx][match_idx][team_idx][1] - 1],
                            ],
                            round_idx,
                            match_idx,
                            team_idx,
                            self._scoreSet,
                        )
                    )
                matches.append(Match(self.nb_point_to_win_match, round_idx, match_idx, teams))
            self._rounds.append(Round(self, round_idx, matches))
        self.save_state()

    @property
    def classement_embed(self) -> disnake.Embed:
        embed = super().classement_embed
        if embed:
            return embed
        sorted_players: List[Player] = self.getRanking()
        ranks = self.rank_emotes(sorted_players)
        return FS.Embed(
            title=self._classement_title,
            color=disnake.Colour.gold(),
            fields=[
                {
                    "name": "🎖️➖__*Joueurs*__",
                    "value": "\n".join([f"{ranks[i]}➖**{p.name}**" for i, p in enumerate(sorted_players)]),
                    "inline": True,
                },
                {
                    "name": FS.Emotes.GEMME_ANIMED,
                    "value": "\n".join([f" **{round(p.points)}**" for p in self.getRanking()]),
                    "inline": True,
                },
                {
                    "name": "➖➖➖➖➖➖➖➖➖➖➖➖➖",
                    "value": f"""> **Calcul des points**
                    > {FS.Emotes.GEMME_ANIMED} Points **=** {self.KILL_EMOTE} Kill  **+**  {self.TURRET_EMOTE} Tour  **+** {self.CS_EMOTE} 100cs
                    > **En cas d'égalité**
                    > {self.KILL_EMOTE} Kill  **>**  {self.TURRET_EMOTE} Tour  **>** {self.CS_EMOTE} 100cs
                    """,
                    "inline": False,
                },
            ],
        )

    @property
    def rounds_embeds(self) -> List[disnake.Embed]:
        embed = super().rounds_embeds
        if embed:
            return [embed]
        return [FS.Embed(title=self._rounds_title)] + [round.embed for round in self.rounds]

    @property
    def rules_embed(self) -> disnake.Embed:
        return FS.Embed(
            title=self._rules_title,
            color=disnake.Colour.purple(),
            fields=[
                {
                    "name": "__**Format du tournoi**__",
                    "value": f"""Le tournoi se joue individuellement mais les matchs se font par **équipe de 2**. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            > ✅ __avec__ chaque autres joueurs exactement :one: fois
                            > ❌ __contre__ chaque autres joueurs exactement :two: fois.
                            Il y aura donc **{self._nb_rounds} rounds**"""
                    + (
                        f"avec **{self._nb_matches_per_round} matchs** en parallèles."
                        if self._nb_matches_per_round > 1
                        else "."
                    ),
                },
                {
                    "name": "__**Format d'un match**__",
                    "value": f"""Les matchs sont en **BO1** se jouant en 2v2 selon le format suivant :
                            > {FS.Emotes.Lol.ARAM} __Map__ : Abime hurlante
                            > Ⓜ️ __Mode__ : Blind
                            > {FS.Emotes.BAN} __Pick & Bans__ : La draft se fait sur discord, via le bot, dans le chat du salon vocal du match. Chaque équipe pourra ban/pick meme temps avec l'ordre suivant : **ban 1** -> **ban 2** -> **pick 1** -> **ban 3** -> **pick 2**
                            Une fois les picks et bans finis, vous obtiendrez un code tournoi à rentrer dans le client (cliquez sur **Jouer**, puis sur le symbole de trophée en haut à droite). Vous devez bien sur respecter les picks établis durant la draft lors de la création de la partie.""",
                },
                {
                    "name": "__**Règles d'un match**__",
                    "value": """> ⛔ __Interdiction__ de prendre les healts **extérieurs** *(ceux entre la **T1** et la **T2**)*.
                            > ✅ __Le suicide__ est autorisé et ne compte pas comme un kill.
                            > ✅ __L'achat d'objet__ lors d'une mort est autorisé.""",
                },
                {
                    "name": "__**Score d'un match**__",
                    "value": f"""Le match se finit lorsque l'une des deux équipes a **2 points**. Une équipe gagne **1 point** pour :
                            > {self.KILL_EMOTE}   __Chaque kills__
                            > {self.TURRET_EMOTE}  __1e tourelle de la game__
                            > {self.CS_EMOTE} __1e joueur d'une équipe à 100cs__""",
                },
                {
                    "name": "__**Score personnel**__",
                    "value": f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur *(indépendamment de qui a marqué le point)*.
                            À la fin des {self._nb_rounds} rounds, c'est les points personnels qui détermineront le classement.""",
                },
                {
                    "name": "__**Égalité**__",
                    "value": f"""En cas d'égalité, on départage avec {self.KILL_EMOTE} **kills** > {self.TURRET_EMOTE} **Tourelles** > {self.CS_EMOTE} **100cs**.
                            En cas d'égalité parfaite pour la 2ième place, un **1v1** en BO1 est organisé *(même règles, mais **1 point** suffit pour gagner)*.""",
                },
                {
                    "name": "__**Tournament finale**__",
                    "value": f"""À la fin des {self._nb_rounds} rounds, un BO5 en **1v1** sera joué entre le **1er** et le **2ième** du classement pour derterminer le grand vainqueur. Pour chaque **{round((self._nb_rounds*2)/5)} point(s)** d'écart, un match d'avance sera accordé au **1er** *(jusqu'à un maximum de 2 matchs d'avance)*.
                    > __*Exemple :*__
                    > **Lỳf** est 1er avec **{self._nb_rounds*2} points** mais **Gay Prime** est 2ième avec **{self._nb_rounds*2-round((self._nb_rounds*2)/5)} points**
                    > ⏭️ **BO5** commençant à **1-0** en faveur de **Lỳf**.""",
                },
            ],
        )

    @classmethod
    def generic_rules(cls) -> disnake.Embed:
        return FS.Embed(
            title=cls._rules_title,
            color=disnake.Colour.purple(),
            fields=[
                {
                    "name": "__**Format du tournoi**__",
                    "value": f"""Le tournoi se joue individuellement mais les matchs se font par **équipe de 2**. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            > ✅ __avec__ chaque autres joueurs exactement :one: fois
                            > ❌ __contre__ chaque autres joueurs exactement :two: fois.""",
                },
                {
                    "name": "__**Format d'un match**__",
                    "value": f"""Les matchs sont en **BO1** se jouant en 2v2 selon le format suivant :
                            > {FS.Emotes.Lol.ARAM} __Map__ : Abime hurlante
                            > Ⓜ️ __Mode__ : Blind
                            > {FS.Emotes.BAN} __Pick & Bans__ : La draft se fait sur discord, via le bot, dans le chat du salon vocal du match. Chaque équipe pourra ban/pick meme temps avec l'ordre suivant : **ban 1** -> **ban 2** -> **pick 1** -> **ban 3** -> **pick 2**
                            Une fois les picks et bans finis, vous obtiendrez un code tournoi à rentrer dans le client (cliquez sur **Jouer**, puis sur le symbole de trophée en haut à droite). Vous devez bien sur respecter les picks établis durant la draft lors de la création de la partie.""",
                },
                {
                    "name": "__**Règles d'un match**__",
                    "value": """> ⛔ __Interdiction__ de prendre les healts **extérieurs** *(ceux entre la **T1** et la **T2**)*.
                            > ✅ __Le suicide__ est autorisé et ne compte pas comme un kill.
                            > ✅ __L'achat d'objet__ lors d'une mort est autorisé.""",
                },
                {
                    "name": "__**Score d'un match**__",
                    "value": f"""Le match se finit lorsque l'une des deux équipes a **2 points**. Une équipe gagne **1 point** pour :
                            > {cls.KILL_EMOTE}   __Chaque kills__
                            > {cls.TURRET_EMOTE}  __1e tourelle de la game__
                            > {cls.CS_EMOTE} __1e joueur d'une équipe à 100cs__""",
                },
                {
                    "name": "__**Score personnel**__",
                    "value": f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur *(indépendamment de qui a marqué le point)*.
                            À la fin des rounds, c'est les points personnels qui détermineront le classement.""",
                },
                {
                    "name": "__**Égalité**__",
                    "value": f"""En cas d'égalité, on départage avec {cls.KILL_EMOTE} **kills** > {cls.TURRET_EMOTE} **Tourelles** > {cls.CS_EMOTE} **100cs**.
                            En cas d'égalité parfaite pour la 2ième place, un **1v1** en BO1 est organisé *(même règles, mais **1 point** suffit pour gagner)*.""",
                },
                {
                    "name": "__**Tournament finale**__",
                    "value": f"""À la fin des rounds, un BO5 en **1v1** sera joué entre le **1er** et le **2ième** du classement pour derterminer le grand vainqueur. Si le **1er** à beaucoup de points d'avance (relativement au nombre de joueur), des match d'avance lui seront accordés *(jusqu'à un maximum de 2 matchs d'avance)*.
                    > __*Exemple d'un tournoi avec 8 joueurs (3 points d'écart = 1 match d'avance):*__
                    > **Lỳf** est 1er avec **14 points** mais **Gay Prime** est 2ième avec **10 points**
                    > ⏭️ **BO5** commençant à **1-0** en faveur de **Lỳf**.""",
                },
            ],
        )

    @property
    def admin_embeds(self) -> List[disnake.Embed]:
        embeds = super().admin_embeds
        if embeds:
            return embeds
        embeds = [FS.Embed(title=self._admin_title)]
        sorted_players: List[Player] = self.getRanking()
        ranks = self.rank_emotes(sorted_players)
        embeds.append(
            FS.Embed(
                title="🏆 __**CLASSEMENT**__🏆 ",
                color=disnake.Colour.gold(),
                fields=[
                    {
                        "name": "🎖️➖__*Joueurs*__",
                        "value": "\n".join([f"{ranks[i]}➖**{p.name}**" for i, p in enumerate(sorted_players)]),
                        "inline": True,
                    },
                    {
                        "name": f"{FS.Emotes.GEMME_ANIMED} __**Points**__",
                        "value": "\n".join(
                            [
                                f"**{round(p.points)}** *({' '.join([str(score) for score in p.scores])})*"
                                for p in sorted_players
                            ]
                        ),
                        "inline": True,
                    },
                    {"name": "➖➖➖➖➖➖➖➖➖➖➖➖➖", "value": f"> MSE = {self.MSE}", "inline": False},
                ],
            )
        )
        embeds += [round.embed_detailled for round in self.rounds]
        return embeds

    async def on_message(self, message: disnake.Message):
        for draftManager in self.draftManagers:
            await draftManager.on_message(message)
