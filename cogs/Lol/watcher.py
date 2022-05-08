from riot_games_api import RiotGamesApi
from riot_games_api.exceptions import RiotGamesApiException
from .exceptions import NoCurrentTeam, SumomnerNotFound
from utils.embed import new_embed
import logging
from disnake import Embed
from datetime import datetime

role_to_emote = {'UNSELECTED':"<:Missing:829247441278074891>",'TOP':'<:Top:797548227004071956>','JUNGLE':'<:Jungle:797548226998829078>','MIDDLE':'<:Mid:797548226944565298>','BOTTOM':'<:Bot:829047436563054632>','UTILITY':'<:Support:797548227347480593>',"FILL":"<:Fill:829062843717386261>"}
rank_to_emote = {'UNRANKED':"<:Unranked:829242191020032001>",'IRON':"<:Iron:829240724871577600>",'BRONZE':"<:Bronze:829240724754792449>",'SILVER':"<:Silver:829240724867514378>",'GOLD':"<:Gold:829240724842872872>",'PLATINUM':"<:Platinum:829240724797128754>",'DIAMOND':"<:Diamond:829240724830027796>",'MASTER':"<:Master:829240724943405096>",'GRANDMASTER':"<:Grandmaster:829240724767768576>",'CHALLENGER':"<:Challenger:829240724712456193>"}


class ClashTeam():

    def __init__(self,team):
        self.name = team.name
        self.abbreviation = team.abbreviation
        self.playersNotSorted = {"TOP":[],"JUNGLE":[],"MIDDLE":[],"BOTTOM":[],"UTILITY":[],"FILL":[],"UNSELECTED":[]}

    def addPlayer(self,player):
        self.playersNotSorted[player.position].append(player)

    def getPlayersSorted(self):
        return self.playersNotSorted["TOP"] + self.playersNotSorted["JUNGLE"] + self.playersNotSorted["MIDDLE"] + self.playersNotSorted["BOTTOM"] + self.playersNotSorted["UTILITY"] + self.playersNotSorted["FILL"] + self.playersNotSorted["UNSELECTED"]


    @property
    def embed(self) -> Embed:
        return new_embed(
            title = "__**{self.name} ({self.abbreviation})**__",
            description = f"\n".join([f"{role_to_emote[p.position]}{rank_to_emote[p.tier]} {player.name}" for p in self.getPlayersSorted()]),
            thumbnail = self.icon
        )
        
    @property
    def opgg(self) -> str:
        return f"https://euw.op.gg/multi/query={''.join([p.name.replace(' ','%20')+'%2C' for p in self.players])}"
    
    @property
    def icon(self) -> str:
        return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/{team.icon_id}/1.png"

class ClashPlayer():

    def __init__(self,player,leagues,name):
        self.name = name
        self.profile_icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{player.summoner_id}.jpg"
        self.position = player.position
        self.tier = 'UNRANKED'
        for league in leagues:
            if league.queue == 'RANKED_SOLO_5x5':
                self.tier = league.tier
                break
        if self.tier == 'UNRANKED':
            for league in leagues:
                if league.queue == 'RANKED_FLEX_SR':
                    self.tier = league.tier
                    break
                

class Watcher(RiotGamesApi):

    def __init__(self,ApiKey):
        super().__init__(ApiKey,"euw1")
       
    def get_clash_team(self,summoner_name:str) -> ClashTeam:
        """
        Return the first clash team for a given summoner_name.
        """
        try:
            summoner = self.summoner.get_summoner_by_name(summoner_name=summoner_name)
            players = self.clash.get_clash_teams(summoner_id=summoner.id)
            if len(players) > 0:
                team = self.clash.get_team(team_id=players[0].team_id)
                clashTeam = ClashTeam(team)
                for player in team.players:
                    summoner = self.summoner.get_summoner_by_account_id(summoner_id=player.summoner_id)
                    leagues = summoner.entries
                    clashTeam.addPlayer(ClashPlayer(player,leagues,summoner.name))
                return clashTeam
            else:
                raise NoCurrentTeam
        except (RiotGamesApiException):
            raise SumomnerNotFound

        