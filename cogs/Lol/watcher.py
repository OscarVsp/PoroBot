from riotwatcher import LolWatcher, ApiError
from .exceptions import NoCurrentTeam, SumomnerNotFound
import modules.FastSnake as FS
import disnake
import asyncio


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
    def embed(self) -> disnake.Embed:
        return FS.Embed(
            title = f"__**{self.name} ({self.abbreviation})**__",
            description = f"\n".join([f"{FS.Emotes.Lol.Position.get(p.position)}{FS.Emotes.Lol.Rank.get(p.tier)} {p.name}" for p in self.getPlayersSorted()]),
            thumbnail = self.icon,
            color = disnake.Colour.blue()
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
        
        