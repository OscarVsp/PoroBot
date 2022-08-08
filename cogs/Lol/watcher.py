from argparse import ArgumentError
from ast import Raise
from typing import Dict, List, Optional, Tuple
from riotwatcher import LolWatcher, ApiError
from .exceptions import LeagueNotFound, NoCurrentTeam, SummonerNotFound, TeamNotFound
import modules.FastSnake as FS
import disnake
import asyncio

TIERS = ['UNRANKED','IRON','BRONZE','SILVER','GOLD','PLATINUM','DIAMOND','MASTER','GRANDMASTER','CHALLENGER']
RANKS = ['N/A','IV','III','II','I']


class Summoner:
    
    def __init__(self, watcher, summoner_name : str = None, encrypted_summoner_id : int = None):
        self.watcher : Watcher = watcher
        if summoner_name == None and id == None:
            raise ArgumentError("Player need at least summoner_name or id to be initialized")
        
        self.name : str = summoner_name
        self.id : str = encrypted_summoner_id
        
    async def fecthData(self):
        
        if self.id:
            try:
                summonerDto : dict = self.watcher.summoner.by_id(self.watcher.region, self.id)
                await asyncio.sleep(0.1)
            except (ApiError):
                raise SummonerNotFound
        else:
            try:
                summonerDto : dict = self.watcher.summoner.by_name(self.watcher.region, self.name)
                await asyncio.sleep(0.1)
                
            except (ApiError):
                raise SummonerNotFound
            
        self.name : str = summonerDto.get('name')
        self.id : str = summonerDto.get('id')
        self.accountid : str = summonerDto.get('accountId')
        self.level = summonerDto.get('summonerLevel')
        self.icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{summonerDto.get('profileIconId')}.jpg"
        
        self.tier : str = 'UNRANKED'
        self.rank : str = 'N/A'
        self.points : int = 0
        try:
            leagues : List[dict]  = self.watcher.league.by_summoner(self.watcher.region, self.id)
            await asyncio.sleep(0.1)
            for league in leagues:
                if league.get('queueType') == 'RANKED_SOLO_5x5':
                    self.tier = league.get('tier')
                    self.rank = league.get('rank')
                    self.points = league.get('leaguePoints')
                    break
            if self.tier == 'UNRANKED':
                for league in leagues:
                    if league.get('queueType') == 'RANKED_FLEX_SR':
                        self.tier = league.get('tier')
                        self.rank = league.get('rank')
                        self.points = league.get('leaguePoints')
                        break
        except (ApiError):
            raise LeagueNotFound
         
    @property       
    def classement(self) -> int:
        return TIERS.index(self.tier)*10000 + RANKS.index(self.rank)*1000 +  self.points
    
    @property
    def tier_emote(self) -> str:
        return FS.Emotes.Lol.Rank.get(self.tier)


class ClashPlayer(Summoner):

    def __init__(self, watcher, playerDto : dict):
        super().__init__(watcher, encrypted_summoner_id=playerDto.get('summonerID'))
        
        self.role : str = playerDto.get('role')
        self.position : str = playerDto.get('position')
        
            
    @property
    def position_emote(self) -> str:
        return FS.Emotes.Lol.Position.get(self.position)

        
                
    

class ClashTeam():

    def __init__(self, watcher, team_id : str = None, summoner : Summoner = None):
        self.watcher : Watcher = watcher
        self.team_id : str = team_id
        self.summoner : Summoner = summoner
        
    async def fetchData(self):
        try:
            if self.team_id:
                teamDto : dict = self.watcher.clash.by_team(self.watcher.region, self.team_id)
                await asyncio.sleep(0.1)
            else:
                listPlayerDto : List[dict] = self.watcher.clash.by_summoner(self.watcher.region, self.summoner.id)
                await asyncio.sleep(0.1)
                if listPlayerDto == []:
                    raise NoCurrentTeam
                teamDto : dict = self.watcher.clash.by_team(self.watcher.region, listPlayerDto[0].get('teamId'))
            self.name = teamDto.get('name')
            self.abbreviation = teamDto.get('abbreviation')
            self.icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/{teamDto.get('iconId')}/1.png"
            self.players : List[ClashPlayer] = []
            for playerDto in teamDto.get('players'):
                new_player = ClashPlayer(self.watcher,playerDto)
                await new_player.fecthData()
                self.players.append(new_player)
            temp : Dict[List[ClashPlayer]] = {"TOP":[],"JUNGLE":[],"MIDDLE":[],"BOTTOM":[],"UTILITY":[],"FILL":[],"UNSELECTED":[],}
            for player in self.players:
                temp[player.position].append(player)
            self.players = temp["TOP"] + temp["JUNGLE"] + temp["MIDDLE"] + temp["BOTTOM"] + temp["UTILITY"] + temp["FILL"] + temp["UNSELECTED"]
        except (ApiError):
            raise TeamNotFound

    @property
    def embed(self) -> disnake.Embed:
        return FS.Embed(
            title = f"__**{self.name} ({self.abbreviation})**__",
            description = f"\n".join([f"{p.position_emote}{p.tier_emote} {p.name}" for p in self.players]),
            thumbnail = self.icon,
            color = disnake.Colour.blue()
        )
        
    @property
    def opgg(self) -> str:
        return f"https://euw.op.gg/multi/query={''.join([p.name.replace(' ','%20')+'%2C' for p in self.players])}"
    
           

class Watcher(LolWatcher):

    def __init__(self,ApiKey : str, region : str = "euw1"):
        super().__init__(ApiKey)
        self.region = region
       
    async def get_clash_team(self,summoner_name:str) -> ClashTeam:
        """
        Return the first clash team for a given summoner_name.
        """
        summoner = await self.get_summoner_by_name(summoner_name)
        clashTeam = ClashTeam(self, summoner=summoner)
        await clashTeam.fetchData()
        return clashTeam
        
    async def get_summoner_by_name(self, summoner_name : str) -> Summoner:
        summoner = Summoner(self, summoner_name=summoner_name)
        await summoner.fecthData()
        return summoner
    