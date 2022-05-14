from riotwatcher import LolWatcher, ApiError
from .exceptions import NoCurrentTeam, SumomnerNotFound
from utils.FastEmbed import FastEmbed
from utils.data import *
import logging
from disnake import Embed
from datetime import datetime
from typing import List
import asyncio


role_to_emote = {'UNSELECTED':"<:Missing:829247441278074891>",'TOP':'<:Top:797548227004071956>','JUNGLE':'<:Jungle:797548226998829078>','MIDDLE':'<:Mid:797548226944565298>','BOTTOM':'<:Bot:829047436563054632>','UTILITY':'<:Support:797548227347480593>',"FILL":"<:Fill:829062843717386261>"}
rank_to_emote = {'UNRANKED':"<:Unranked:829242191020032001>",'IRON':"<:Iron:829240724871577600>",'BRONZE':"<:Bronze:829240724754792449>",'SILVER':"<:Silver:829240724867514378>",'GOLD':"<:Gold:829240724842872872>",'PLATINUM':"<:Platinum:829240724797128754>",'DIAMOND':"<:Diamond:829240724830027796>",'MASTER':"<:Master:829240724943405096>",'GRANDMASTER':"<:Grandmaster:829240724767768576>",'CHALLENGER':"<:Challenger:829240724712456193>"}

class ClashPlayer():

    def __init__(self, player, summoner, leagues):
        self.name = summoner.get('name')
        self.profile_icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{summoner.get('profileIconId')}.jpg"
        self.position = player.get('position')
        self.tier = 'UNRANKED'
        for league in leagues:
            if league.get('queueType') == 'RANKED_SOLO_5x5':
                self.tier = league.get('tier')
                break
        if self.tier == 'UNRANKED':
            for league in leagues:
                if league.get('queueType') == 'RANKED_FLEX_SR':
                    self.tier = league.get('tier')
                    break

class ClashTeam():

    def __init__(self,team):
        self.name = team.get('name')
        self.abbreviation = team.get('abbreviation')
        self._icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/{team.get('iconId')}/1.png"
        self.playersNotSorted = {"TOP":[],"JUNGLE":[],"MIDDLE":[],"BOTTOM":[],"UTILITY":[],"FILL":[],"UNSELECTED":[]}

    def addPlayer(self,player : ClashPlayer):
        self.playersNotSorted[player.position].append(player)

    def getPlayersSorted(self):
        return self.playersNotSorted["TOP"] + self.playersNotSorted["JUNGLE"] + self.playersNotSorted["MIDDLE"] + self.playersNotSorted["BOTTOM"] + self.playersNotSorted["UTILITY"] + self.playersNotSorted["FILL"] + self.playersNotSorted["UNSELECTED"]

    @property
    def embed(self) -> Embed:
        return FastEmbed(
            title = f"__**{self.name} ({self.abbreviation})**__",
            description = f"\n".join([f"{role_to_emote[p.position]}{rank_to_emote[p.tier]} {p.name}" for p in self.getPlayersSorted()]),
            thumbnail = self.icon,
            color = color.bleu
        )
        
    @property
    def opgg(self) -> str:
        return f"https://euw.op.gg/multi/query={''.join([p.name.replace(' ','%20')+'%2C' for p in self.getPlayersSorted()])}"
    
    @property
    def icon(self) -> str:
        return self._icon
           

class Watcher(LolWatcher):

    def __init__(self,ApiKey : str, region : str = "euw1"):
        super().__init__(ApiKey)
        self.region = region
       
    async def get_clash_team(self,summoner_name:str) -> ClashTeam:
        """
        Return the first clash team for a given summoner_name.
        """
        try:
            summoner = self.summoner.by_name(self.region, summoner_name)
            await asyncio.sleep(0.1)
            players = self.clash.by_summoner(self.region, summoner.get('id'))
            await asyncio.sleep(0.1)
            if len(players) > 0:
                team = self.clash.by_team(self.region, players[0].get('teamId'))
                await asyncio.sleep(0.1)
                clashTeam : ClashTeam = ClashTeam(team)
                for player in team.get('players'):
                    summoner = self.summoner.by_id(self.region, player.get('summonerId'))
                    await asyncio.sleep(0.1)
                    leagues = self.league.by_summoner(self.region, summoner.get('id'))
                    await asyncio.sleep(0.1)
                    clashTeam.addPlayer(ClashPlayer(player, summoner, leagues))
                return clashTeam
            raise NoCurrentTeam
        except (ApiError):
            raise SumomnerNotFound
        
        