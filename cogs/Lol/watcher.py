from pyot.models import lol
from pyot.core import Settings
from requests.exceptions import HTTPError
from exceptions import *
import logging
from disnake import Embed
from datetime import datetime

role_to_emote = {'UNSELECTED':"<:Missing:829247441278074891>",'TOP':'<:Top:797548227004071956>','JUNGLE':'<:Jungle:797548226998829078>','MIDDLE':'<:Mid:797548226944565298>','BOTTOM':'<:Bot:829047436563054632>','UTILITY':'<:Support:797548227347480593>',"FILL":"<:Fill:829062843717386261>"}
rank_to_emote = {'UNRANKED':"<:Unranked:829242191020032001>",'IRON':"<:Iron:829240724871577600>",'BRONZE':"<:Bronze:829240724754792449>",'SILVER':"<:Silver:829240724867514378>",'GOLD':"<:Gold:829240724842872872>",'PLATINUM':"<:Platinum:829240724797128754>",'DIAMOND':"<:Diamond:829240724830027796>",'MASTER':"<:Master:829240724943405096>",'GRANDMASTER':"<:Grandmaster:829240724767768576>",'CHALLENGER':"<:Challenger:829240724712456193>"}


class ClashTeam():

    def __init__(self,team):
        self.name = team.name
        self.abbreviation = team.abbreviation
        self.icon = f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/{team.icon_id}/1.png"
        self.opgg = "https://euw.op.gg/multi/query="
        self.playersNotSorted = {"TOP":[],"JUNGLE":[],"MIDDLE":[],"BOTTOM":[],"UTILITY":[],"FILL":[],"UNSELECTED":[]}

    def addPlayer(self,player):
        self.playersNotSorted[player.position].append(player)
        self.opgg += player.name.replace(' ','%20')+'%2C'

    def getPlayersSorted(self):
        return self.playersNotSorted["TOP"] + self.playersNotSorted["JUNGLE"] + self.playersNotSorted["MIDDLE"] + self.playersNotSorted["BOTTOM"] + self.playersNotSorted["UTILITY"] + self.playersNotSorted["FILL"] + self.playersNotSorted["UNSELECTED"]


    def toEmbed(self):
        text = ""
        for player in self.getPlayersSorted():
            text += role_to_emote[player.position] + rank_to_emote[player.tier] +" "+player.name + " \n"
        return Embed(title=f"<:Opgg:829260989404020776> __**{self.name} ({self.abbreviation})**__ <:Opgg:829260989404020776>",description=text,url=self.opgg).set_thumbnail(url=self.icon)

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
class ChampionLore():

    def __init__(self,champion,api_name,lore_name,image_name):
        self.lore_name = lore_name
        self.image_name = image_name
        self.api_name = api_name
        self.name = champion.full_name
        if self.name == "":
            self.name = champion.name
        self.icon = "https://ddragon.leagueoflegends.com/cdn/11.7.1/img/champion/"+image_name+".png"
        self.splash = "http://ddragon.leagueoflegends.com/cdn/img/champion/splash/"+image_name+"_0.jpg"
        self.lore = champion.lore
        self.lore_link = "https://universe.leagueoflegends.com/en_GB/champion/"+lore_name+"/"

    def toEmbed(self):
        return Embed(description="*"+self.lore+"*\n [__Voir le lore complet__]("+self.lore_link+")").set_image(url=self.splash).set_author(name=self.name,icon_url=self.icon)

class Watcher():

    def __init__(self,ApiKey):
        Settings(
            MODEL = "LOL",
            DEFAULT_PLATFORM = "EUW1",
            DEFAULT_REGION = "EUROPE",
            DEFAULT_LOCALE= "FR_FR",
            PIPELINE = [
                {"BACKEND": "pyot.stores.Omnistone"},
                {"BACKEND": "pyot.stores.MerakiCDN"},
                {"BACKEND": "pyot.stores.CDragon"},
                {
                    "BACKEND": "pyot.stores.RiotAPI",
                    "API_KEY": ApiKey
                }
            ]
        ).activate()
       
    async def get_clash_team(self,summoner_name:str):
        """
        Return the first clash team for a given summoner_name.
        """
        try:
            summoner = await lol.Summoner(name=summoner_name).get()
            players = (await lol.ClashPlayers(summoner_id=summoner.id).get()).players
            if len(players) > 0:
                team = (await lol.ClashTeam(id=players[0].team_id).get())
                clashTeam = ClashTeam(team)
                for player in team.players:
                    leagues = (await lol.SummonerLeague(summoner_id=player.summoner_id).get()).entries
                    if len(leagues) == 0:
                        name = (await lol.Summoner(id=player.summoner_id).get()).name
                    else:
                        name = leagues[0].summoner_name
                    clashTeam.addPlayer(ClashPlayer(player,leagues,name))
                return clashTeam
            else:
                raise NoCurrentTeam
        except (NotFound):
            raise DataNotFound
        except (RateLimited):
            raise BeingRateLimited
        except (ServerError) as se:
            raise se

    def championFormat(self,name):

        close = {
            "kaisa":"kai'sa",
            "khazix":"kha'zix",
            "chogath":"cho'gath",
            "kogmaw":"kog'maw",
            "reksai":"rek'sai",
            "velkoz":"vel'koz",
            "mundo":"dr. mundo",
            "dr.mundo":"dr. mundo",
            "nunu et willump":"nunu",
            "nunu & willump":"nunu"}
        special = {
            "jarvan iv":{'api':'Jarvan IV','url_lore':'jarvaniv','url_image':'JarvanIV'},
            "nunu":{'api':'Nunu & Willump','url_lore':'nunu','url_image':'Nunu'}}

        def formatApi(name):
            name = name[0].upper() + name[1:].lower()
            nameTemp = ''
            nextUp = False
            for l in name:
                if l in [" ","'"]:
                    nameTemp += l
                    nextUp = True
                elif nextUp:
                    nameTemp += l.upper()
                    nextUp = False
                else:
                    nameTemp += l
            return nameTemp

        def formatLore(name):
            name = name.lower()
            return name.replace(" ","").replace("'","").replace(".","")

        def formatImage(name):
            lore_exception = {
                "kog'maw":"KogMaw"
            }
            if name in lore_exception.keys():
                return lore_exception[name]
            name = name[0].upper() + name[1:].lower()
            nameTemp = ''
            nextUp = False
            for l in name:
                if l in [" ","'","."]:
                    if l in [" ","."]:
                        nextUp = True
                elif nextUp:
                    nameTemp += l.upper()
                    nextUp = False
                else:
                    nameTemp += l
            return nameTemp

        if name.lower() in close.keys():
            name = close[name.lower()]
        if name.lower() in special.keys():
            return special[name.lower()]
        else:
            return (formatApi(name),formatLore(name),formatImage(name))
        
    async def lore(self,champion):
        """
        champion : str, trad : boolean  ->  champion : ChampionClash     
        """
        (api_name,lore_name,image_name) = self.championFormat(champion)
        try:
            return ChampionLore((await lol.MerakiChampion(name=api_name).get()),api_name,lore_name,image_name)
        except (NotFound):
            raise DataNotFound
        except (RateLimited):
            raise BeingRateLimited
        except (ServerError) as se:
            raise se

        