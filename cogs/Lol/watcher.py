from typing import Dict, List, Optional
from riotwatcher import LolWatcher, ApiError
from .exceptions import LeagueNotFound, MasteriesNotFound, SummonerNotFound, TeamNotFound, WatcherNotInit
import modules.FastSnake as FS
import disnake
import asyncio


class Watcher:

    REGION = "euw1"
    WATCHER = None

    @classmethod
    def init(cls, api_key: str):
        cls.WATCHER = LolWatcher(api_key=api_key)

    @property
    def watcher(self) -> LolWatcher:
        if self.WATCHER:
            return self.WATCHER
        raise WatcherNotInit

    @property
    def region(self) -> str:
        return self.REGION

    @classmethod
    def get_watcher(cls):
        if cls.WATCHER:
            return cls.WATCHER
        raise WatcherNotInit


class Leagues(Watcher):

    class QueueType:
        RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
        RANKED_FLEX_SR = "RANKED_FLEX_SR"

    TIERS = ['UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD',
             'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    RANKS = ['-', 'IV', 'III', 'II', 'I']
    

    class League:

        def __init__(self, leagueEntryDto: dict):
            self._leagueEntryDto: dict = leagueEntryDto
            self.leagueId: str = leagueEntryDto.get('leagueId')
            self.summonerId: str = leagueEntryDto.get('summonerId')
            self.summonerName: str = leagueEntryDto.get('summonerName')
            self.queueType: str = leagueEntryDto.get('queueType')
            self.tier: str = leagueEntryDto.get('tier')
            self.rank: str = leagueEntryDto.get('rank')
            self.leaguePoints: int = leagueEntryDto.get('leaguePoints')
            self.wins: int = leagueEntryDto.get('wins')
            self.losses: int = leagueEntryDto.get('losses')
            self.hotStreak: bool = leagueEntryDto.get('hotStreak')
            self.veteran: bool = leagueEntryDto.get('veteran')
            self.freshBlood: bool = leagueEntryDto.get('freshBlood')
            self.inactive: bool = leagueEntryDto.get('inactive')
            self.miniSeries = leagueEntryDto.get('miniSeries')
            
        @staticmethod
        def default(queueType: str):
            return Leagues.League({
                'queueType':queueType,
                'tier':Leagues.TIERS[0],
                'rank':Leagues.RANKS[0],
                'leaguePoints':0
            })

        @property
        def absolut_score(self) -> int:
            return Leagues.TIERS.index(self.tier)*10000 + Leagues.RANKS.index(self.rank)*1000 + self.leaguePoints

        @property
        def tier_emote(self) -> str:
            return FS.Emotes.Lol.Rank.get(self.tier)

    def __init__(self, listLeagueEntryDto: dict):
        self._listLeagueEntryDto: List[dict] = listLeagueEntryDto
        self.solo : Leagues.League = None
        self.flex : Leagues.League = None
        for leagueEntryDto in listLeagueEntryDto:
            new_league = Leagues.League(leagueEntryDto)
            if new_league.queueType == Leagues.QueueType.RANKED_SOLO_5x5:
                self.solo = new_league
            elif new_league.queueType == Leagues.QueueType.RANKED_FLEX_SR:
                self.flex = new_league
        if self.solo == None:
            self.sol = Leagues.League.default(Leagues.QueueType.RANKED_SOLO_5x5)
        if self.flex == None:
            self.flex = Leagues.League.default(Leagues.QueueType.RANKED_FLEX_SR)

    @classmethod
    async def by_summoner_id(cls, summoner_id: str):
        try:
            listLeagueEntryDto: dict = cls.get_watcher(
            ).league.by_summoner(cls.REGION, summoner_id)
            await asyncio.sleep(0.1)
            return Leagues(listLeagueEntryDto)
        except (ApiError):
            raise LeagueNotFound

    @property
    def highest(self) -> Optional[League]:
        if self.solo and self.flex:
            if self.solo.absolut_score > self.flex.absolut_score:
                return self.solo
        elif self.solo:
            return self.solo
        elif self.flex:
            return self.flex
        return None

    @property
    def first(self) -> Optional[League]:
        if self.solo and self.flex:
            if self.solo.tier == Leagues.RANKS[0]:
                return self.flex
            return self.solo
        elif self.solo:
            return self.solo
        elif self.flex:
            return self.flex
        return None


class CurrentGame(Watcher):

    class Perks:

        def __init__(self, perksInfo: dict):
            self._perksInfo: dict = perksInfo
            self.perkIds: List[int] = perksInfo.get('perkIds')
            self.perkStyle: int = perksInfo.get('perkIds')
            self.perkSubStyle: int = perksInfo.get('perkSubStyle')

    class CustomizationObject:

        def __init__(self, customizationObjectInfo: dict):
            self._customizationObjectInfo: dict = customizationObjectInfo
            self.category: str = customizationObjectInfo.get('category')
            self.content: str = customizationObjectInfo.get('content')

    class Participant:

        def __init__(self, participantInfo: dict):
            self._participantInfo: dict = participantInfo
            self.championId: int = participantInfo.get('championId')
            self.perks: CurrentGame.Perks = CurrentGame.Perks(
                participantInfo.get('perks'))
            self.profileIconId: int = participantInfo.get('profileIconId')
            self.bot: bool = participantInfo.get('bot')
            self.teamId: int = participantInfo.get('teamId')
            self.summonerName: int = participantInfo.get('summonerName')
            self.summonerId: int = participantInfo.get('summonerId')
            self.spell1Id: int = participantInfo.get('spell1Id')
            self.spell2Id: int = participantInfo.get('spell2Id')
            self.gameCustomizationObjects: List[CurrentGame.CustomizationObject] = [CurrentGame.CustomizationObject(
                customizationObjectInfo) for customizationObjectInfo in participantInfo.get('gameCustomizationObjects')]

    class BannedChampion:

        def __init__(self, bannedChampionInfo: dict):
            self._bannedChampionInfo: dict = bannedChampionInfo
            self.pickTurn: int = bannedChampionInfo.get('pickTurn')
            self.championId: int = bannedChampionInfo.get('championId')
            self.teamId: int = bannedChampionInfo.get('teamId')

    def __init__(self, CurrentGameInfo: dict):
        self._CurrentGameInfo: dict = CurrentGameInfo
        self.gameId: int = CurrentGameInfo.get('gameId')
        self.gameType: str = CurrentGameInfo.get('gameType')
        self.gameStartTime: int = CurrentGameInfo.get('gameStartTime')
        self.mapId: int = CurrentGameInfo.get('mapId')
        self.gameLength: int = CurrentGameInfo.get('gameLength')
        self.platformId: int = CurrentGameInfo.get('platformId')
        self.gameMode: str = CurrentGameInfo.get('gameMode')
        self.bannedChampions: List[CurrentGame.BannedChampion] = [CurrentGame.BannedChampion(
            bannedChampionInfo) for bannedChampionInfo in CurrentGameInfo.get("bannedChampions")]
        self.gameQueueConfigId: int = CurrentGameInfo.get('gameQueueConfigId')
        self.observers_key: str = (CurrentGameInfo.get(
            "observers")).get('encryptionKey')
        self.participants: List[CurrentGame.Participant] = [CurrentGame.Participant(
            participantInfo) for participantInfo in CurrentGameInfo.get("participants")]

    @classmethod
    async def by_summoner(cls, summoner_id: str):
        try:
            currentGameInfo = cls.get_watcher().spectator.by_summoner(cls.REGION, summoner_id)
            await asyncio.sleep(0.1)
            return CurrentGame(currentGameInfo)
        except (ApiError):
            return None


class ChampionMastery(Watcher):

    def __init__(self, championMasteryDto: dict):
        self._championMasteryDto: dict = championMasteryDto
        self.id: int = championMasteryDto.get("championId")
        self.level: int = championMasteryDto.get('championLevel')
        self.point: int = championMasteryDto.get('championPoints')
        self.pointToNextLevel: int = championMasteryDto.get(
            'championPointsUntilNextLevel')
        self.pointSinceLastLevel: int = championMasteryDto.get(
            'championPointsSinceLastLevel')
        self.chest: bool = championMasteryDto.get('chestGranted')
        self.lastPlayTime: int = championMasteryDto.get('lastPlayTime')
        self.level: int = championMasteryDto.get('championLevel')
        self.currentToken: int = championMasteryDto.get('tokensEarned')

    @classmethod
    async def by_summoner_and_champion(cls, encrypted_summoner_id: str, champion_id: str):
        if cls.WATCHER:
            championMasteryDto = cls.WATCHER.champion_mastery.by_summoner_by_champion(
                encrypted_summoner_id=encrypted_summoner_id, champion_id=champion_id)
            await asyncio.sleep(0.1)
            return ChampionMastery(championMasteryDto)
        raise WatcherNotInit


class Masteries(Watcher):

    def __init__(self, listChampionMasteryDto):
        self._listChampionMasteryDto: List[dict] = listChampionMasteryDto
        self.champions: List[ChampionMastery] = []
        for championMasteryDto in listChampionMasteryDto:
            self.champions.append(ChampionMastery(championMasteryDto))

    @classmethod
    async def by_summoner(cls, id: str):
        try:
            listChampionMasteryDto: List[dict] = cls.get_watcher(
            ).champion_mastery.by_summoner(cls.REGION, id)
            await asyncio.sleep(0.1)
            return Masteries(listChampionMasteryDto)
        except (ApiError):
            MasteriesNotFound


class Summoner(Watcher):

    def __init__(self, summonerDto: dict):
        self._summonerDto: dict = summonerDto
        self.name: str = summonerDto.get('name')
        self.revisionDate: int = summonerDto.get('revisionDate')
        self.id: str = summonerDto.get('id')
        self.puuid = str = summonerDto.get('puuid')
        self.accountid: str = summonerDto.get('accountId')
        self.summonerLevel = summonerDto.get('summonerLevel')
        self.profileIconId = summonerDto.get('profileIconId')

        self.icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{self.profileIconId}.jpg"

        self._leagues: Leagues = None
        self._masteries: Masteries = None
        self._currentGame: CurrentGame = None
        self._lastGame: CurrentGame = None

    @classmethod
    async def by_name(cls, summoner_name: str):
        try:
            summonerDto: dict = cls.get_watcher().summoner.by_name(cls.REGION, summoner_name)
            await asyncio.sleep(0.1)
            return Summoner(summonerDto)
        except (ApiError):
            raise SummonerNotFound

    @classmethod
    async def by_id(cls, summoner_id: str):
        try:
            summonerDto: dict = cls.get_watcher().summoner.by_id(cls.REGION, summoner_id)
            await asyncio.sleep(0.1)
            return Summoner(summonerDto)
        except (ApiError):
            return None

    async def leagues(self, force_request: bool = False) -> Leagues:
        if self._leagues == None or force_request:
            self._leagues = await Leagues.by_summoner_id(self.id)
        return self._leagues

    async def masteries(self, force_request: bool = False) -> Masteries:
        if self._masteries == None or force_request:
            self._masteries = await Masteries.by_summoner(self.id)
        return self._masteries

    async def currentGame(self, force_request: bool = True) -> Optional[CurrentGame]:
        if self._currentGame == None or force_request:
            if force_request:
                self._lastGame = self._currentGame
            self._currentGame = await CurrentGame.by_summoner(self.id)
        return self._currentGame

    def lastGame(self) -> Optional[CurrentGame]:
        return self._lastGame


class ClashPlayer(Summoner):

    def __init__(self, playerDto: dict, summonerDto: dict):
        super().__init__(summonerDto)
        self._playerDto: dict = playerDto
        self.role: str = playerDto.get('role')
        self.position: str = playerDto.get('position')
        self.teamId: str = playerDto.get('teamId')
        self.summonerId: str = playerDto.get('summonerId')

        self.position_emote: str = FS.Emotes.Lol.Position.get(self.position)

    @classmethod
    async def by_name(cls, summoner_name: str):
        return await cls.by_summoner(await super().by_name(summoner_name))

    @classmethod
    async def by_summoner(cls, summoner: Summoner):
        listPlayerDto: dict = cls.get_watcher().clash.by_summoner(cls.REGION, summoner.id)
        await asyncio.sleep(0.1)
        if len(listPlayerDto) > 0:
            return ClashPlayer(listPlayerDto[0], summoner=summoner._summonerDto)
        return None

    @classmethod
    async def by_Dto(cls, playerDto: dict):
        try:
            summonerDto: dict = cls.get_watcher().summoner.by_id(
                cls.REGION, playerDto.get('summonerId'))
            await asyncio.sleep(0.1)
            return ClashPlayer(playerDto, summonerDto)
        except (ApiError):
            raise SummonerNotFound


class ClashTeam(Watcher):

    def __init__(self, TeamDto: dict):
        self._TeamDto: dict = TeamDto
        self.id: str = TeamDto.get('id')
        self.tournamentId: int = TeamDto.get('tournamentId')
        self.name: str = TeamDto.get('name')
        self.iconId: int = TeamDto.get('iconId')
        self.tier: int = TeamDto.get('tier')
        self.captain: str = TeamDto.get('captain')
        self.abbreviation: str = TeamDto.get('abbreviation')
        self.icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/{self.iconId}/1.png"
        self.listPlayerDto: dict = TeamDto.get('players')
        self._players: List[ClashPlayer] = None

    async def players(self, force_request: bool = False) -> List[ClashPlayer]:
        if self._players == None or force_request:
            temp: Dict[List[ClashPlayer]] = {"TOP": [], "JUNGLE": [], "MIDDLE": [
            ], "BOTTOM": [], "UTILITY": [], "FILL": [], "UNSELECTED": []}
            for playerDto in self.listPlayerDto:
                clash_player = await ClashPlayer.by_Dto(playerDto)
                temp[clash_player.position].append(clash_player)
            self._players = temp["TOP"] + temp["JUNGLE"] + temp["MIDDLE"] + \
                temp["BOTTOM"] + temp["UTILITY"] + \
                temp["FILL"] + temp["UNSELECTED"]

        return self._players

    @classmethod
    async def by_id(cls, team_id: str):
        try:
            teamDto: dict = cls.get_watcher().clash.by_team(cls.REGION, team_id)
            await asyncio.sleep(0.1)
            return ClashTeam(teamDto)
        except (ApiError):
            raise TeamNotFound

    @classmethod
    async def by_summoner_name(cls, summoner_name: str):
        player: ClashPlayer = await ClashPlayer.by_name(summoner_name)
        if player:
            return await cls.by_id(player.teamId)
        return None

    async def embed(self) -> disnake.Embed:
        return FS.Embed(
            title=f"__**{self.name} ({self.abbreviation})**__",
            description=f"\n".join([f"{p.position_emote}{(await p.leagues()).first.tier_emote} {p.name}" for p in (await self.players())]),
            thumbnail=self.icon,
            color=disnake.Colour.blue()
        )

    async def opgg(self) -> str:
        return f"https://euw.op.gg/multi/query={''.join([p.name.replace(' ','%20')+'%2C' for p in (await self.players())])}"
