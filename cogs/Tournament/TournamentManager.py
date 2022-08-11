from typing import List
from modules.FastSnake.Views import memberSelection
from .classes import *
from .view import TournamentView


class Tournament(TournamentData):

    def __init__(self, guild: disnake.Guild, name: str, size: int, nb_round: int = None, nb_matches_per_round: int = None, nb_teams_per_match: int = None, nb_players_per_team: int = None, size_of_scores: int = 1, weigths: List[float] = [1], scores_descriptor: List[str] = None, score_emoji: List[str] = None,  nb_point_to_win_match: int = 2):
        super().__init__(guild, name, size, nb_round, nb_matches_per_round, nb_teams_per_match,
                         nb_players_per_team, size_of_scores, weigths, scores_descriptor, score_emoji,  nb_point_to_win_match)
        self.admin_view: TournamentView = None

    async def build(self) -> None:
        self.category = await self.guild.create_category(self.name.upper())
        cat_perm_everyone = disnake.PermissionOverwrite()
        cat_perm_everyone.send_messages = False
        cat_perm_everyone.connect = True
        await self.category.set_permissions(self.everyone, overwrite=cat_perm_everyone)
        self.notif_channel = await self.category.create_text_channel(name="🔔 Annonces")
        self.classement_channel = await self.category.create_text_channel(name="🏅 Classement")
        self.rounds_channel = await self.category.create_text_channel(name="📅 Rounds")
        self.rules_channel = await self.category.create_text_channel(name="📜 Règles")
        self.admin_channel = await self.category.create_text_channel(name="🔧 Admin")
        voice_perm = disnake.PermissionOverwrite()
        voice_perm.connect = True
        voice_perm.send_messages = True
        self.voice_general = await self.category.create_text_channel(name="🏆 General")
        await self.voice_general.set_permissions(self.everyone, overwrite=voice_perm)
        for i in range(self._nb_matches_per_round):
            self.voice_channels.append([])
            for j in range(self._nb_teams_per_match):
                if self._nb_matches_per_round == 1:
                    name = f"Team {j+1}"
                else:
                    name = f"Match {chr(ord('A') + i)} Team {j+1}"
                self.voice_channels[i].append(await self.category.create_voice_channel(name=name))

        self.classement_message = await self.classement_channel.send(embed=self.classement_embed)
        self.rounds_message = await self.rounds_channel.send(embeds=self.rounds_embeds)
        self.rules_message = await self.rules_channel.send(embed=self.rules_embed)
        

    async def set_players(self) -> None:
        selection = await memberSelection(target=self.admin_channel,title=self._admin_title,description="Sélectionner les participants",size=self.size)#custom View for it
        if selection:
            self._players = selection.members
            await self.generate()
            self.admin_view = TournamentView(self)
            self.admin_message = await self.admin_message.edit(embeds=self.admin_embeds,view=self.admin_view)
            await self.update()
        else:
            await self.delete()
        

    async def generate(self) -> None:
        pass

    async def update(self) -> None:
        self.classement_message = await self.classement_message.edit(embed=self.classement_embed)
        self.rounds_message = await self.rounds_message.edit(embeds=self.rounds_embeds)
        self.rules_message = await self.rules_message.edit(embed=self.rules_embed)
        
    async def set_score(self, round: Union[Round, int], match: Union[Match, int], entity: Union[Entity, int], value: int = 1, index: int = 0) -> None:
        super().set_score(round, match, entity, value, index)
        await self.update()

    async def set_scores(self, round: Union[Round, int], match: Union[Match, int], entity: Union[Entity, int], values: List[int]) -> None:
        super().set_scores(round, match, entity, values)
        await self.update()

    async def send_notif(self, title: str, description: str) -> None:
        self.notif_messages.append(await self.notif_channel.send(FS.Embed(
            author_name=f"{self.name.upper()}",
            author_icon_url=FS.Assets.Images.Tournament.Trophy,
            title=title,
            description=description,
            color=disnake.Colour.blue()
        )))

    async def delete(self) -> None:
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


class Tournament2v2Roll(Tournament):

    class Score:
        KILLS: int = 0
        TURRETS: int = 1
        CS: int = 2

    class Seeding:
        S4: List[List[List[List[int]]]] = [
            [
                [[2, 3], [1, 4]]
            ], [
                [[1, 3], [2, 4]]
            ], [
                [[1, 2], [3, 4]]
            ]
        ]

        S5: List[List[List[List[int]]]] = [
            [
                [[4, 5], [2, 3]]
            ], [
                [[1, 3], [2, 4]]
            ], [
                [[1, 5], [3, 4]]
            ], [
                [[2, 5], [1, 4]]
            ], [
                [[1, 2], [3, 5]]
            ]
        ]

        S8: List[List[List[List[int]]]] = [
            [
                [[3, 4], [7, 8]],
                [[5, 6], [1, 2]]
            ], [
                [[6, 8], [5, 7]],
                [[1, 3], [2, 4]]
            ], [
                [[1, 4], [5, 8]],
                [[6, 7], [2, 3]]
            ], [
                [[4, 8], [2, 6]],
                [[3, 7], [1, 5]]
            ], [
                [[3, 8], [1, 6]],
                [[2, 5], [4, 7]]
            ], [
                [[2, 8], [3, 5]],
                [[4, 6], [1, 7]]
            ], [
                [[1, 8], [2, 7]],
                [[4, 5], [3, 6]]
            ]
        ]

    def __init__(self, guild: disnake.Guild, size: int, name: str = "2v2 Roll"):

        if size == 4:
            self._seeding: List[List[List[List[int]]]
                                ] = Tournament2v2Roll.Seeding.S4
        elif size == 5:
            self._seeding: List[List[List[List[int]]]
                                ] = Tournament2v2Roll.Seeding.S5
        elif size == 8:
            self._seeding: List[List[List[List[int]]]
                                ] = Tournament2v2Roll.Seeding.S8

        super().__init__(
            guild,
            name,
            size,
            nb_round=len(self._seeding),
            nb_matches_per_round=len(self._seeding[0]),
            nb_teams_per_match=len(self._seeding[0][0]),
            nb_players_per_team=len(self._seeding[0][0][0]),
            size_of_scores=3,
            weigths=[1.001, 1, 0.989],
            scores_descriptor=["kill(s)", "turret(s)", "cs"],
            score_emoji=["⚔️", "🧱", "🧙‍♂️"],
            nb_point_to_win_match=2
        )

    def generate(self) -> None:
        if self.players == None:
            raise PlayersNotSetError
        self.shuffle_players()
        self._rounds = []
        for round_idx in range(self._nb_rounds):
            matches = []
            for match_idx in range(self._nb_matches_per_round):
                teams = []
                for team_idx in range(2):
                    teams.append(Team(self, [self._players[self._seeding[round_idx][match_idx][team_idx][0]-1],
                                 self._players[self._seeding[round_idx][match_idx][team_idx][1]-1]], round_idx, match_idx, team_idx, 3))
                matches.append(Match(self, round_idx, match_idx, teams))
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
                    'name': "🎖️➖__*Joueurs*__",
                    'value': "\n".join([f"{ranks[i]}➖**{p.display}**" for i, p in enumerate(sorted_players)]),
                    'inline':True
                },
                {
                    'name': "💎",
                    'value': "\n".join([f" **{round(p.points)}**" for p in self.getRanking()]),
                    'inline':True
                },
                {
                    'name': "➖➖➖➖➖➖➖➖➖➖➖➖➖",
                    'value': """> **Calcul des points**
                    > 💎 Points **=** ⚔️ Kill  **+**  🧱 Tour  **+**  🧙‍♂️ 100cs
                    > **En cas d'égalité**
                    > ⚔️ Kill  **>**  🧱 Tour  **>**  🧙‍♂️ 100cs
                    """,
                    'inline': False
                }
            ]
        )

    @property
    def rounds_embeds(self) -> List[disnake.Embed]:
        embed = super().rounds_embeds
        if embed:
            return [embed]
        return [FS.Embed(title=self._rounds_title)]+[round.embed for round in self.rounds]

    @property
    def rules_embed(self) -> disnake.Embed:
        return FS.Embed(
            title=self._rules_title,
            color=disnake.Colour.purple(),
            fields=[
                {
                    'name': "__**Format du tournoi**__",
                    'value': f"""Le tournoi se joue individuellement mais les matchs se font par **équipe de 2**. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            > ✅ __avec__ chaque autres joueurs exactement :one: fois
                            > :x: __contre__ chaque autres joueurs exactement :two: fois.
                            Il y aura donc **{self._nb_rounds} rounds**"""+(f"avec **{self._nb_matches_per_round} matchs** en parallèles." if self._nb_matches_per_round > 1 else ".")
                },
                {
                    'name': "__**Format d'un match**__",
                    'value': """Les matchs sont en **BO1** se jouant en 2v2 selon le format suivant :
                            > 🌍 __Map__ : Abime hurlante
                            > 👓 __Mode__ : Blind
                            > ❌ __Bans__ : 3 par équipe *(à faire via le chat dans le lobby **pré-game**)*"""
                },
                {
                    'name': "__**Règles d'un match**__",
                    'value': """> ⛔ __Interdiction__ de prendre les healts **extérieurs** *(ceux entre la **T1** et la **T2**)*.
                            > ✅ __Le suicide__ est autorisé et ne compte pas comme un kill.
                            > ✅ __L'achat d'objet__ lors d'une mort est autorisé."""
                },
                {
                    'name': "__**Score d'un match**__",
                    'value': """Le match se finit lorsque l'une des deux équipes a **2 points**. Une équipe gagne **1 point** pour :
                            > ⚔️  __Chaque kills__
                            > 🧱 __1e tourelle de la game__
                            > 🧙‍♂️ __1e joueur d'une équipe à 100cs__"""
                },
                {
                    'name': "__**Score personnel**__",
                    'value': f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur *(indépendamment de qui a marqué le point)*.
                            À la fin des {self._nb_rounds} rounds, c'est les points personnels qui détermineront le classement."""
                },
                {
                    'name': "__**Égalité**__",
                    'value': f"""En cas d'égalité, on départage avec ⚔️ **kills** > 🧱 **Tourelles** > 🧙‍♂️ **100cs**.
                            En cas d'égalité parfaite pour la 2ième place, un **1v1** en BO1 est organisé *(même règles, mais **1 point** suffit pour gagner)*."""
                },
                {
                    'name': "__**Tournament finale**__",
                    'value': f"""À la fin des {self._nb_rounds} rounds, un BO5 en **1v1** sera joué entre le **1er** et le **2ième** du classement pour derterminer le grand vainqueur. Pour chaque **{round((self._nb_rounds*2)/5)} point(s)** d'écart, un match d'avance sera accordé au **1er** *(jusqu'à un maximum de 2 matchs d'avance)*.
                    > __*Exemple :*__
                    > **Lỳf** est 1er avec **{self._nb_rounds*2} points** mais **Gay Prime** est 2ième avec **{self._nb_rounds*2-round((self._nb_rounds*2)/5)} points**
                    > ⏭️ **BO5** commençant à **1-0** en faveur de **Lỳf**."""
                }
            ]
        )

    @property
    def admin_embeds(self) -> List[disnake.Embed]:
        embed = super().admin_embeds
        if embed:
            return [embed]
        embeds = [FS.Embed(title=self._admin_title)] + \
            [round.embed_detailled for round in self.rounds]
        sorted_players: List[Player] = self.getRanking()
        ranks = self.rank_emotes(sorted_players)
        embeds.append(FS.Embed(
            title="🏆 __**CLASSEMENT**__🏆 ",
            color=disnake.Colour.gold(),
            fields=[
                {
                    'name': "🎖️➖__*Joueurs*__",
                    'value': "\n".join([f"{ranks[i]}➖**{p.display}**" for i, p in enumerate(sorted_players)]),
                    'inline':True
                },
                {
                    'name': "💎 __**Points**__",
                    'value': "\n".join([f"**{round(p.points)}** *({p.scores[self.Score.KILLS]}  {p.scores[self.Score.TURRETS]}  {p.scores[self.Score.CS]})*" for p in self.getRanking()]),
                    'inline':True
                },
                {
                    'name': "➖➖➖➖➖➖➖➖➖➖➖➖➖",
                    'value': f"> MSE = {self.MSE}",
                    'inline': False
                }
            ]
        ))
        return embeds
