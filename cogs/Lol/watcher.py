from bz2 import decompress
import os
from typing import Dict, List, Optional
from unittest.loader import VALID_MODULE_NAME

import modules.FastSnake as FS
import disnake

from pyot.conf.model import activate_model, ModelConf
from pyot.conf.pipeline import activate_pipeline, PipelineConf
from pyot.core.exceptions import *
from pyot.core.queue import Queue

from pyot.utils.lol.champion import *


@activate_model("lol")
class LolModel(ModelConf):
    default_platform = "euw1"
    default_region = "europe"
    default_version = "latest"
    default_locale = "en_us"


@activate_pipeline("lol")
class LolPipeline(PipelineConf):
    name = "lol_main"
    default = True
    stores = [
        {
            "backend": "pyot.stores.omnistone.Omnistone",
            "expirations": {
                "summoner_v4_by_name": 120,
                "match_v4_match": 600,
                "match_v4_timeline": 600,
            }
        },
        {
            "backend": "pyot.stores.cdragon.CDragon",
        },
        {
            "backend": "pyot.stores.merakicdn.MerakiCDN",
        },
        {
            "backend": "pyot.stores.riotapi.RiotAPI",
            "api_key": os.getenv("RIOT_APIKEY"),
        }
    ]


from pyot.models import lol

class SummonerLeague(lol.SummonerLeague):
    
    class Queue:
        RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
        RANKED_FLEX_SR = "RANKED_FLEX_SR"
    
    TIERS = ['UNRANKED', 'IRON', 'BRONZE', 'SILVER', 'GOLD',
             'PLATINUM', 'DIAMOND', 'MASTER', 'GRANDMASTER', 'CHALLENGER']
    RANKS = ['-', 'IV', 'III', 'II', 'I']
    
    class Meta(lol.SummonerLeague.Meta):
        pass
    
        
    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)
    
    ################""
    
    @staticmethod
    def sorting_score(entry : lol.league.SummonerLeagueEntryData):
        return SummonerLeague.TIERS.index(entry.tier)*10000 + SummonerLeague.RANKS.index(entry.rank)*1000 + entry.league_points
    
    @property
    def solo(self) -> Optional[lol.league.SummonerLeagueEntryData]:
        for entry in self.entries:
            if entry.queue == SummonerLeague.Queue.RANKED_SOLO_5x5:
                return entry
        return None
    
    @property
    def flex(self) -> Optional[lol.league.SummonerLeagueEntryData]:
        for entry in self.entries:
            if entry.queue == SummonerLeague.Queue.RANKED_FLEX_SR:
                return entry
        return None
    
    @property
    def highest(self) -> Optional[lol.league.SummonerLeagueEntryData]:
        scoring = [self.sorting_score(entry) for entry in self.entries]
        return self.entries[scoring.index(max(scoring))]
    
    @property
    def first(self) -> Optional[lol.league.SummonerLeagueEntryData]:
        if self.solo:
            return self.solo
        return self.flex
    
    def league_to_line(self, league : lol.league.SummonerLeagueEntryData) -> str:
        return f"{FS.Emotes.Lol.Tier.get(league.tier)} **{league.rank}** *({league.league_points} LP)*"
       
    @property 
    def field(self) -> dict:
        value = ""
        if self.solo:
            value += f"> **Solo/Duo :** {self.league_to_line(self.solo)}"
            if self.flex:
                value+="\n"
        if self.flex:
            value += f"> **Flex :** {self.league_to_line(self.flex)}"
        if value == "":
            value = "*No Ranked Data*"
        return {
            'name':f'{FS.Emotes.Lol.Tier.NONE} **RANKED**',
            'value':value
        }
    
class ChampionMasteries(lol.ChampionMasteries):
    
    class Meta(lol.ChampionMasteries.Meta):
        pass
    
    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)
    
    ###########################
    
    def champion_by_name(self, name : str) -> lol.ChampionMastery:
        return next((mastery for mastery in self.masteries if mastery.champion.name == name))
    
    def top(self, n : int = 3) -> List[lol.ChampionMastery]:
        self.masteries.sort(key=lambda m: (m.champion_level, m.champion_points), reverse=True)
        return [self.masteries[i] for i in range(min(n,len(self.masteries)))]
    
    def field(self, n : int = 3) -> dict:
        top = self.top(n=n)
        return {
            'name':f"{FS.Emotes.Lol.MASTERIES[0]} **MASTERIES**",
            'value':("\n".join([f"> {self.champion_to_line(champ)}" for champ in top]) if len(top) > 0 else f"{FS.Emotes.Lol.MASTERIES[0]} *Aucune maitrise*")
        }
    
    def champion_to_line(self, champion : lol.ChampionMastery) -> str:
        return f"{FS.Emotes.Lol.MASTERIES[champion.champion_level]} **{FS.Emotes.Lol.Champions.get(champion.champion_id)}** *{self.champion_points_formatted(champion)}*"
    
    def champion_points_formatted(self, champion : lol.ChampionMastery) -> str:
        num = float('{:.3g}'.format(champion.champion_points))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])
    
class ClashPlayers(lol.ClashPlayers):
    
    class Meta(lol.ClashPlayers.Meta):
        pass
    
    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)
    
class ClashTeam(lol.ClashTeam):
    
    _icon_url : str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/"
    _opgg_url : str = "https://euw.op.gg/multi/query="
    
    class Meta(lol.ClashTeam.Meta):
        pass
    
    @property
    def captain(self) -> "Summoner":
        return Summoner(id=self.captain_summoner_id, platform=self.platform)
    
    @property
    def tournament(self) -> "ClashTournament":
        return super().tournament
    
    
    #################
    
    @property
    def tierFormatted(self) -> str:
        return 'I'*self.tier if self.tier != 4 else "IV"
    
    @property
    def sortedPlayers(self) -> List[lol.clash.ClashPlayerData]:
        temp: Dict[List[lol.clash.ClashPlayerData]] = {"TOP": [], "JUNGLE": [], "MIDDLE": [
        ], "BOTTOM": [], "UTILITY": [], "FILL": [], "UNSELECTED": []}
        for player in self.players:
            temp[player.position].append(player)
        return temp["TOP"] + temp["JUNGLE"] + temp["MIDDLE"] + \
            temp["BOTTOM"] + temp["UTILITY"] + \
            temp["FILL"] + temp["UNSELECTED"]
            
    @property
    def icon_url(self) -> str:
        return self._icon_url+self.icon_id+"/1.png"
    
    @async_property
    async def opgg_url(self) -> str:
        return self._opgg_url+''.join([(await p.summoner.get()).name.replace(' ','%20')+'%2C' for p in self.players])
               
    @async_property
    async def embed(self) -> disnake.Embed:
        description =f"Tier **{self.tierFormatted}**\n\n"
        for player in self.sortedPlayers:
            summoner = await Summoner(id=player.summoner_id).get()
            league = await summoner.league_entries.get()
            description += f"> {FS.Emotes.Lol.Positions.get(player.position)}{FS.Emotes.Lol.Ranks.get(league.first.rank)} {summoner.name}"
            if player.role == "CAPTAIN":
                description += f" {FS.Emotes.Lol.CAPTAIN}"
            description += "\n"
        return FS.Embed(
            title=f"__**{self.name} [{self.abbreviation.upper()}]**__",
            description=description,
            thumbnail=self.icon_url,
            color=disnake.Colour.blue()
        )
    
class ClashTournament(lol.ClashTournament):
    
    class Meta(lol.ClashTournament.Meta):
        pass
    
    @property
    def team(self) -> ClashTeam:
        return ClashTeam(id=self.team_id, platform=self.platform)
    
    
class Summoner(lol.Summoner):
    
    _icon_url : str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
    _opgg_url : str = "https://euw.op.gg/summoners/euw/"
    
    class Meta(lol.Summoner.Meta):
        pass
    
    @property
    def champion_masteries(self) -> "ChampionMasteries":
        return ChampionMasteries(summoner_id=self.id, platform=self.platform)
    
    @property
    def clash_players(self) -> "ClashPlayers":
        return ClashPlayers(summoner_id=self.id, platform=self.platform)  
    
    @property
    def current_game(self) -> "lol.CurrentGame":
        return super().current_game     #TODO
    
    @property
    def league_entries(self) -> "SummonerLeague":
        return SummonerLeague(summoner_id=self.id, platform=self.platform)
    
    ####
    
    @property
    def icon_url(self) -> str:
        return self._icon_url+str(self.profile_icon_id)+".jpg"
    
    @property
    def opgg_url(self) -> str:
        return self._opgg_url+self.name.replace(' ','%20')
    
    @async_property
    async def embed(self) -> disnake.Embed:
        championMasteries = await self.champion_masteries.get()
        summonerLeague = await self.league_entries.get()
        return FS.Embed(
            author_name=f"{self.name.upper()}",
            description=f"{FS.Emotes.Lol.XP} **LEVEL**\n> **{self.level}**",
            color=disnake.Colour.blue(),
            author_icon_url=self.icon_url,
            fields=[
                championMasteries.field(),
                summonerLeague.field
            ]
        )

class Champion(lol.Champion):
    
    class Meta(lol.Champion.Meta):
        pass
    
    @property
    def meraki_champion(self) -> "lol.MerakiChampion":
        return lol.MerakiChampion(id=self.id)
    
    
class MerakiChampion(lol.MerakiChampion):
    
    class Meta(lol.MerakiChampion.Meta):
        pass
    
    @property
    def meraki_champion(self) -> "lol.Champion":
        return Champion(key=self.key, locale="en_us")
    
    ###############
    
    def stat_to_line(self, stat : lol.merakichampion.MerakiChampionStatDetailData):
        if stat.flat:
            if stat.per_level:
                return f"**{stat.flat}** + *{stat.per_level}/lvl* ➖ **{round(stat.flat+stat.per_level*18)}** at lvl. 18"
            else:
                return f"**{stat.flat}**"
        elif stat.percent:
            if stat.percent_per_level:
                return f"**{stat.percent}%** + *{stat.percent_per_level}%/lvl* ➖ **{round(stat.percent+stat.percent_per_level*18)}%** at lvl. 18"
            else:
                return f"**{stat.percent}%**"
        else:
            return "*N/A*"
    
    @property
    def stats_embed(self) -> disnake.Embed:
        return FS.Embed(
            title="__**Stats**__",
            description=f"**Dammage type:** `{self.adaptive_type.split('_')[0]}`\n**Attack type:** `{self.attack_type}`\n**Roles:** "+" ".join([f"{FS.Emotes.Lol.Roles.get(role)}" for role in self.roles]),
            fields = [
                {
                    'name':"➖",
                    'value':f"""{FS.Emotes.Lol.Stats.HEALT} ➖ {self.stat_to_line(self.stats.health)}
                                {FS.Emotes.Lol.Stats.MANA} ➖ {self.stat_to_line(self.stats.mana)}
                                {FS.Emotes.Lol.Stats.ARMOR} ➖ {self.stat_to_line(self.stats.armor)}
                                {FS.Emotes.Lol.Stats.ATTACKSPEED} ➖ {self.stat_to_line(self.stats.attack_speed)}
                                {FS.Emotes.Lol.Stats.MOVESPEED} ➖ {self.stat_to_line(self.stats.movespeed)}""",
                    'inline':True
                },
                {
                    'name':"➖",
                    'value':f"""{FS.Emotes.Lol.Stats.HEALTREGEN} ➖ {self.stat_to_line(self.stats.health_regen)}
                                {FS.Emotes.Lol.Stats.MANAREGEN} ➖ {self.stat_to_line(self.stats.mana_regen)}
                                {FS.Emotes.Lol.Stats.MAGICRESISTE} ➖ {self.stat_to_line(self.stats.magic_resistance)}
                                {FS.Emotes.Lol.Stats.ATTACKDAMAGE} ➖ {self.stat_to_line(self.stats.attack_damage)}
                                {FS.Emotes.Lol.Stats.RANGE} ➖ {self.stat_to_line(self.stats.attack_range)}""",
                    'inline':True
                }
            ]
        )
        
    def ability_detailled_embed(self, letter : str) -> List[disnake.Embed]: 
        if letter == "P":
            abilities = self.abilities.p
        elif letter == "Q":
            abilities = self.abilities.q
        elif letter == "W":
            abilities = self.abilities.w
        elif letter == "E":
            abilities = self.abilities.e
        elif letter == "R":
            abilities = self.abilities.r
        else:
            return None
        
        embeds : List[disnake.Embed] = []
        
        for ability in abilities:
            
            embed = FS.Embed(title=f"__**{letter.upper()} - {ability.name}**__",thumbnail=ability.icon)
            embed.add_field(name="Cost",value=(f"{FS.Emotes.Lol.Stats.Ressource(ability.resource)} *"+ "/".join([f"{ability.cost.modifiers[0].values[i]}{ability.cost.modifiers[0].units[i]}" for i in range(len(ability.cost.modifiers[0].values))])+"*" if ability.resource else "*--*"))
            embed.add_field(name="Cooldown",value=(f"{FS.Emotes.Lol.Stats.ABILITYHASTE} *"+ "/".join([f"{ability.cooldown.modifiers[0].values[i]}{ability.cooldown.modifiers[0].units[i]}" for i in range(len(ability.cooldown.modifiers[0].values))])+"*" if ability.resource else "*--*"))        #Add minition recharge ?
            embed.add_field(name="Range",value=f"{FS.Emotes.Lol.TargetType.get(ability.targeting)} "+(f"*{ability.target_range}*" if ability.target_range else (f"*{ability.effect_radius}*" if ability.effect_radius else "*--*")))        #Add zone type ?            
            
            for effect in ability.effects:      #TODO Better modifier format for the case of constant value (only once)
                description = f"**{effect.description}**"
                for attr in effect.leveling:
                    description += f"\n__{attr.attribute} :__\n"
                    if attr.modifiers and len(attr.modifiers) > 0:
                        for i in range(len(attr.modifiers[0].values)):
                            description += "`"+"".join([f"({attr.modifiers[j].values[i]}{attr.modifiers[j].units[i]})" for j in range(len(attr.modifiers))]) + "`**/**"
                    description = description[:-5]
                embed.add_field(name="➖",value=description, inline=False)
                
            block : str = ""
            if ability.on_target_cd_static:
                block += f"> **Per target cd:** {FS.Emotes.Lol.Stats.ABILITYHASTE} `{ability.on_target_cd_static}`\n"
            if ability.targeting:
                block += f"> **Target type:** `{ability.targeting}`\n"
            if ability.spell_effects:
                block += f"> **Effect type:** `{ability.spell_effects}`\n"
            if ability.width:
                block += f"> **Width:** `{ability.width}`\n"
            if ability.effect_radius:
                block += f"> **Effect Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.effect_radius}`\n"
            if ability.tether_radius:
                block += f"> **Tether Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.tether_radius}`\n"
            if ability.inner_radius:
                block += f"> **Inner Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.inner_radius}`\n"
            if ability.collision_radius:
                block += f"> **Collision Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.collision_radius}`\n"
            if ability.damage_type:
                block += f"> **Damage type:** `{ability.damage_type}`\n"
            if ability.affects:
                block += f"> **Affects:** `{ability.affects}`\n"
            if ability.spellshieldable:
                block += f"> **Spellshieldable:** `{ability.spellshieldable}`\n"
            if ability.projectile:
                block += f"> **Projectile:** `{ability.projectile}`\n"
            if ability.missile_speed:
                block += f"> **Missile speed:** `{ability.missile_speed}`\n"
            if ability.on_hit_effects:
                block += f"> **On hit effects:** `{ability.on_hit_effects}`\n"
            if ability.occurrence:
                block += f"> **Occurence:** `{ability.occurrence}`\n"
            if ability.cast_time:
                block += f"> **Cast time:** `{ability.cast_time}`\n"
            embed.add_field(name="**__DETAILS__**",value=block)
            
            embeds.append(embed)
        return embeds

    

        
    def ability_embed(self, letter : str, ability : lol.merakichampion.MerakiChampionSpellData) -> disnake.Embed:
        return FS.Embed(
            title=f"__**{letter.upper()} - {ability.name}**__",
            description=f"> {ability.blurb}",
            thumbnail=ability.icon
        )        

    @property
    def abilities_embeds(self) -> List[disnake.Embed]:
        return [self.ability_embed("p",p) for p in self.abilities.p]+[self.ability_embed("q",q) for q in self.abilities.q]+[self.ability_embed("w",w) for w in self.abilities.w]+[self.ability_embed("e",e) for e in self.abilities.e]+[self.ability_embed("r",r) for r in self.abilities.r]
    
    @property
    def BaseEmbed(self) -> disnake.Embed:
        return FS.Embed(
            author_name=self.full_name if self.full_name else self.name,
            title=f"*{self.title}*",
            author_icon_url=self.skins[0].tile_path
            )
        
    @property
    def embeds(self) -> List[disnake.Embed]:
        embeds = [self.BaseEmbed.add_field(name="➖",value=f"> *{self.lore}*", inline=False)]
        embeds.append(self.stats_embed)
        embeds += self.abilities_embeds
        return embeds
    

    @property
    def Pembeds(self) -> List[disnake.Embed]:
        return [self.BaseEmbed] + self.ability_detailled_embed("P")
    
    @property
    def Qembeds(self) -> List[disnake.Embed]:
        return [self.BaseEmbed] + self.ability_detailled_embed("Q")
    
    @property
    def Wembeds(self) -> List[disnake.Embed]:
        return [self.BaseEmbed] + self.ability_detailled_embed("W")
    
    @property
    def Eembeds(self) -> List[disnake.Embed]:
        return [self.BaseEmbed] + self.ability_detailled_embed("E")
    
    @property
    def Rembeds(self) -> List[disnake.Embed]:
        return [self.BaseEmbed] + self.ability_detailled_embed("R")