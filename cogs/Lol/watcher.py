import time
from typing import Dict, List, Optional
from riotwatcher import LolWatcher, ApiError
from .exceptions import LeagueNotFound, MasteriesNotFound, SummonerNotFound, TeamNotFound, WatcherNotInit
import modules.FastSnake as FS
import disnake
import asyncio
import requests
import json


class Watcher:

    REGION: str = "euw1"
    WATCHER: LolWatcher = None
    VERSION: str = None
    CHAMPIONS: dict = {}
    QUEUETYPE : List[dict] = []
    QUEUES : List[dict] = []
    MAPS : List[dict] = []


    @classmethod
    def init(cls, api_key: str):
        cls.WATCHER = LolWatcher(api_key=api_key)
        cls.VERSION = json.loads(requests.get(
            "https://ddragon.leagueoflegends.com/api/versions.json").text)[0]
        cls.CHAMPIONS = json.loads(requests.get(
            f"https://ddragon.leagueoflegends.com/cdn/{cls.VERSION}/data/en_US/champion.json").text).get('data')
        cls.QUEUETYPE = json.loads(requests.get(
            f"https://static.developer.riotgames.com/docs/lol/queues.json").text)
        cls.MAPS = json.loads(requests.get(
            f"https://static.developer.riotgames.com/docs/lol/maps.json").text)
        cls.QUEUES = json.loads(requests.get(
            f"https://static.developer.riotgames.com/docs/lol/queues.json").text)


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

    @classmethod
    def champion_name_from_id(cls, champion_id: int) -> str:
        for champion in cls.CHAMPIONS.values():
            if champion.get('key') == str(champion_id):
                return champion.get('name')
        return f"Unknown (id: {champion_id})"
            
    @classmethod
    def maps_name_from_id(cls, map_id : int) -> str:
        for map in cls.MAPS:
            if map.get('mapID') == map_id:
                return map.get('mapName')
        return f"Unknown (id: {map_id})"
    
    @classmethod
    def queue_dict_from_id(cls, queue_id : int) -> dict:
        for queue in cls.QUEUES:
            if queue.get('queueId') == queue_id:
                return queue
        return {'map':'UNKNOWN MAP','description':'UNKNOWN GAME'}



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
                'queueType': queueType,
                'tier': Leagues.TIERS[0],
                'rank': Leagues.RANKS[0],
                'leaguePoints': 0
            })

        @property
        def absolut_score(self) -> int:
            return Leagues.TIERS.index(self.tier)*10000 + Leagues.RANKS.index(self.rank)*1000 + self.leaguePoints

        @property
        def tier_emote(self) -> str:
            return FS.Emotes.Lol.Ranks.get(self.tier)

    def __init__(self, listLeagueEntryDto: dict):
        self._listLeagueEntryDto: List[dict] = listLeagueEntryDto
        self.solo: Leagues.League = None
        self.flex: Leagues.League = None
        for leagueEntryDto in listLeagueEntryDto:
            new_league = Leagues.League(leagueEntryDto)
            if new_league.queueType == Leagues.QueueType.RANKED_SOLO_5x5:
                self.solo = new_league
            elif new_league.queueType == Leagues.QueueType.RANKED_FLEX_SR:
                self.flex = new_league
        if self.solo == None:
            self.solo = Leagues.League.default(
                Leagues.QueueType.RANKED_SOLO_5x5)
        if self.flex == None:
            self.flex = Leagues.League.default(
                Leagues.QueueType.RANKED_FLEX_SR)

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
        if self.solo.absolut_score > self.flex.absolut_score:
            return self.solo
        return self.flex

    @property
    def first(self) -> Optional[League]:
        if self.solo.absolut_score > 0:
            return self.solo
        return self.flex


class CurrentGame(Watcher):

    class Perks:

        def __init__(self, perksInfo: dict):
            self._perksInfo: dict = perksInfo
            self.perkIds: List[int] = perksInfo.get('perkIds')
            self.perkStyle: int = perksInfo.get('perkIds')
            self.perkSubStyle: int = perksInfo.get('perkSubStyle')
        
        @property    
        def emote(self) -> str:
            return FS.Emotes.Lol.Rune.NONE
        
        @property    
        def subEmote(self) -> str:
            return FS.Emotes.Lol.Rune.NONE

    class CustomizationObject:

        def __init__(self, customizationObjectInfo: dict):
            self._customizationObjectInfo: dict = customizationObjectInfo
            self.category: str = customizationObjectInfo.get('category')
            self.content: str = customizationObjectInfo.get('content')
            
    class Team:
        
        def __init__(self, team_id : int) -> None:
            self.bannedChampions : List[CurrentGame.BannedChampion] = []
            self.participants : List[CurrentGame.Participant] = []
            self.id : int = team_id
            
        @property
        def bans_block(self) -> str:
            return "\n".join([f"> `{b.name}`" for b in self.bannedChampions])
        
        async def participants_block(self) -> str:
            return "\n".join([f"> {(await (await p.summoner()).leagues()).first.tier_emote} **{p.summonerName if len(p.summonerName) < 15 else p.summonerName[:15]}** - `{p.championName}`" for p in self.participants])
            
        @property
        def opgg(self) -> str:
            return f"https://euw.op.gg/multi/query={''.join([p.summonerName.replace(' ','%20')+'%2C' for p in self.participants])}"

        
    class Participant:

        def __init__(self, participantInfo: dict):
            self._participantInfo: dict = participantInfo
            self.championId: str = str(participantInfo.get('championId'))
            self.perks: CurrentGame.Perks = CurrentGame.Perks(
                participantInfo.get('perks'))
            self.profileIconId: int = participantInfo.get('profileIconId')
            self.bot: bool = participantInfo.get('bot')
            self.teamId: int = participantInfo.get('teamId')
            self.summonerName: str = participantInfo.get('summonerName')
            self.summonerId: str = participantInfo.get('summonerId')
            self.spell1Id: int = participantInfo.get('spell1Id')
            self.spell2Id: int = participantInfo.get('spell2Id')
            self.gameCustomizationObjects: List[CurrentGame.CustomizationObject] = [CurrentGame.CustomizationObject(
                customizationObjectInfo) for customizationObjectInfo in participantInfo.get('gameCustomizationObjects')]
            
            self.championName : str = Watcher.champion_name_from_id(self.championId)
            
            self._summoner : Summoner = None
            
        async def summoner(self, force_update : bool = False):
            if self._summoner == None or force_update:
                self._summoner = await Summoner.by_id(self.summonerId)
            return self._summoner

    class BannedChampion:

        def __init__(self, bannedChampionInfo: dict):
            self._bannedChampionInfo: dict = bannedChampionInfo
            self.pickTurn: int = bannedChampionInfo.get('pickTurn')
            self.championId: int = bannedChampionInfo.get('championId')
            self.teamId: int = bannedChampionInfo.get('teamId')

            self.name: str = Watcher.champion_name_from_id(self.championId) if self.championId > 0 else "-"
            

    def __init__(self, CurrentGameInfo: dict):
        self._currentGameInfo: dict = CurrentGameInfo
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
        
        self.teams : List[CurrentGame.Team] = []
        for participant in self.participants:
            team = next((team for team in self.teams if team.id == participant.teamId), None)
            if team == None:
                team = CurrentGame.Team(participant.teamId)
                self.teams.append(team)
            team.participants.append(participant)
            
        for bannedChampion in self.bannedChampions:
            team = next((team for team in self.teams if team.id == bannedChampion.teamId), None)
            team.bannedChampions.append(bannedChampion)
            
        for team in self.teams:
            team.bannedChampions.sort(key=lambda b:b.pickTurn)
        
        self.gameLengthFormatted : str = time.strftime("%M:%S", time.gmtime(self.gameLength))
        
        queue : dict = self.queue_dict_from_id(self.gameQueueConfigId)
        self.mapName : str = queue.get('map')
        self.gameName : str = queue.get('description')[4:]
        
        if self.mapName == "Summoner's Rift":
            self.mapImage : str = FS.Images.Lol.RIFT
            self.mapIcon : str = FS.Emotes.Lol.RIFT
        elif self.mapName == "Howling Abyss":
            self.mapImage : str = FS.Images.Lol.ARAM
            self.mapIcon : str = FS.Emotes.Lol.ARAM
        else:
            self.mapImage : str = None
            
        
            
            
    @classmethod
    async def by_summoner(cls, summoner_id: str):
        try:
            currentGameInfo = cls.get_watcher().spectator.by_summoner(cls.REGION, summoner_id)
            await asyncio.sleep(0.1)
            return CurrentGame(currentGameInfo)
        except (ApiError):
            return None
        
    
    async def embed(self) -> disnake.Embed:
        embed = FS.Embed(
            title=f"{FS.Emotes.Lol.LOGO} __**GAME EN COURS**__",
            description=f"**Map :** `{self.mapName}` {self.mapIcon}\n**Type :** `{self.gameName}`\n**Durée :** `{self.gameLengthFormatted}`",
            color=disnake.Colour.blue()
        )
        for i,team in enumerate(self.teams):
            embed.add_field(
                name=f"**__TEAM {FS.Emotes.Num(i+1)}__**",
                value=f"{(await team.participants_block())}"+(f"\n**__BANS__**\n{team.bans_block}" if team.bans_block != "" else "")+f"\n[opgg]({team.opgg})"
            )
        return embed

class ChampionMastery(Watcher):

    def __init__(self, championMasteryDto: dict):
        self._championMasteryDto: dict = championMasteryDto
        self.championId: str = str(championMasteryDto.get("championId"))
        self.championLevel: int = championMasteryDto.get('championLevel')
        self.championPoints: int = championMasteryDto.get('championPoints')
        self.championPointsUntilNextLevel: int = championMasteryDto.get(
            'championPointsUntilNextLevel')
        self.championPointsSinceLastLevel: int = championMasteryDto.get(
            'championPointsSinceLastLevel')
        self.chestGranted: bool = championMasteryDto.get('chestGranted')
        self.lastPlayTime: int = championMasteryDto.get('lastPlayTime')
        self.currentToken: int = championMasteryDto.get('tokensEarned')

        self.name: str = Watcher.champion_name_from_id(self.championId)
        num = float('{:.3g}'.format(self.championPoints))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        self.championPointsFormatted: str = '{}{}'.format('{:f}'.format(
            num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    @classmethod
    async def by_summoner_and_champion(cls, encrypted_summoner_id: str, champion_id: str):
        if cls.WATCHER:
            championMasteryDto = cls.WATCHER.champion_mastery.by_summoner_by_champion(
                encrypted_summoner_id=encrypted_summoner_id, champion_id=champion_id)
            await asyncio.sleep(0.1)
            return ChampionMastery(championMasteryDto)
        raise WatcherNotInit

    @property
    def line_description(self) -> str:
        return f"{FS.Emotes.Lol.MASTERIES[self.championLevel]} **{self.name}** *({self.championPointsFormatted})*"


class Masteries(Watcher):

    def __init__(self, listChampionMasteryDto : dict):
        self._listChampionMasteryDto: List[dict] = listChampionMasteryDto
        self.champions: List[ChampionMastery] = []
        for championMasteryDto in listChampionMasteryDto:
            self.champions.append(ChampionMastery(championMasteryDto))
        self.champions.sort(key=lambda x: x.championPoints, reverse=True)

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
        self.opgg = f"https://euw.op.gg/summoners/euw/{self.name.replace(' ','%20')}"

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

    async def leagues(self, force_update: bool = False) -> Leagues:
        if self._leagues == None or force_update:
            self._leagues = await Leagues.by_summoner_id(self.id)
        return self._leagues

    async def masteries(self, force_update: bool = False) -> Masteries:
        if self._masteries == None or force_update:
            self._masteries = await Masteries.by_summoner(self.id)
        return self._masteries

    async def currentGame(self, force_update: bool = True) -> Optional[CurrentGame]:
        if self._currentGame == None or force_update:
            if force_update:
                self._lastGame = self._currentGame
            self._currentGame = await CurrentGame.by_summoner(self.id)
        return self._currentGame

    def lastGame(self) -> Optional[CurrentGame]:
        return self._lastGame

    async def embed(self, force_update : bool = False) -> disnake.Embed:
        embed = FS.Embed(
            description=f"{FS.Emotes.Lol.XP} **LEVEL**\n> **{self.summonerLevel}**",
            author_icon_url=FS.Images.Lol.LOGO,
            author_url=self.opgg,
            author_name=self.name,
            color=disnake.Colour.blue(),
            thumbnail=self.icon
        )
        if force_update:
            await self.leagues(force_update=True)
            await self.masteries(force_update=True)
        if self._masteries:
            embed.add_field(
                name=f'{FS.Emotes.Lol.MASTERIES[0]} **MASTERIES**',
                value=("\n".join([f"> {self._masteries.champions[i].line_description}" for i in range(min(3,len(self._masteries.champions)))]) if len(self._masteries.champions) > 0 else f"{FS.Emotes.Lol.MASTERIES[0]} *Aucune maitrise*"),
                inline=False
            )
        if self._leagues or force_update:
            leagues = (await self.leagues())
            embed.add_field(
                name=f'{FS.Emotes.Lol.Ranks.NONE} **RANKED**',
                value=f"> **Solo/Duo :** {leagues.solo.tier_emote} **{leagues.solo.rank}** *({leagues.solo.leaguePoints} LP)*\n> **Flex :** {leagues.flex.tier_emote} **{leagues.flex.rank}** *({leagues.flex.leaguePoints} LP)*",
                inline=False
            )
        return embed

class ClashPlayer(Summoner):

    def __init__(self, playerDto: dict, summonerDto: dict):
        super().__init__(summonerDto)
        self._playerDto: dict = playerDto
        self.role: str = playerDto.get('role')
        self.position: str = playerDto.get('position')
        self.teamId: str = playerDto.get('teamId')
        self.summonerId: str = playerDto.get('summonerId')

        self.position_emote: str = FS.Emotes.Lol.Positions.get(self.position)

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
    async def by_summoner_id(cls, summoner_id : int):
        return await cls.by_summoner(await super().by_id(summoner_id))

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

    async def players(self, force_update: bool = False) -> List[ClashPlayer]:
        if self._players == None or force_update:
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
    
    @classmethod
    async def by_summoner_id(cls, summoner_id: str):
        player: ClashPlayer = await ClashPlayer.by_summoner_id(summoner_id)
        if player:
            return await cls.by_id(player.teamId)
        return None
    
    @classmethod
    async def by_summoner(cls, summoner: Summoner):
        player: ClashPlayer = await ClashPlayer.by_summoner(summoner)
        if player:
            return await cls.by_id(player.teamId)
        return None

    async def embed(self) -> disnake.Embed:
        return FS.Embed(
            title=f"__**{self.name} ({self.abbreviation})**__",
            description=f"\n".join([f"{p.position_emote}{(await p.leagues()).first.tier_emote} {p.name}"+(" "+FS.Emotes.Lol.CAPTAIN if p.summonerId == self.captain else "") for p in (await self.players())]),
            thumbnail=self.icon,
            color=disnake.Colour.blue()
        )

    async def opgg(self) -> str:
        return f"https://euw.op.gg/multi/query={''.join([p.name.replace(' ','%20')+'%2C' for p in (await self.players())])}"
