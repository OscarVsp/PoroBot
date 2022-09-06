# -*- coding: utf-8 -*-
import json
import logging
import os
from math import ceil
from time import gmtime
from time import strftime
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

import disnake
import requests
from pyot.conf.model import activate_model
from pyot.conf.model import ModelConf
from pyot.conf.pipeline import activate_pipeline
from pyot.conf.pipeline import PipelineConf
from pyot.core.exceptions import *
from pyot.utils.lol.champion import *

import modules.FastSnake as FS


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
            },
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
        },
    ]


from pyot.models import lol

queuesData: List[dict] = json.loads(requests.get(f"https://static.developer.riotgames.com/docs/lol/queues.json").text)

mapsData: List[dict] = json.loads(requests.get(f"https://static.developer.riotgames.com/docs/lol/maps.json").text)


class SummonerLeague(lol.SummonerLeague):
    class Queue:
        RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
        RANKED_FLEX_SR = "RANKED_FLEX_SR"

    TIERS = [
        "UNRANKED",
        "IRON",
        "BRONZE",
        "SILVER",
        "GOLD",
        "PLATINUM",
        "DIAMOND",
        "MASTER",
        "GRANDMASTER",
        "CHALLENGER",
    ]
    RANKS = ["-", "IV", "III", "II", "I"]

    class Meta(lol.SummonerLeague.Meta):
        pass

    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)

    @staticmethod
    def sorting_score(entry: lol.league.SummonerLeagueEntryData):
        if entry:
            return (
                SummonerLeague.TIERS.index(entry.tier) * 10000
                + SummonerLeague.RANKS.index(entry.rank) * 1000
                + entry.league_points
            )
        return 0

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

    def league_to_line(self, league: lol.league.SummonerLeagueEntryData) -> str:
        if league:
            return f"{self.short(league)} *{league.league_points} LP*"
        return f"{FS.Emotes.Lol.Tier.get('UNRANKED')}{FS.Emotes.Lol.Rank.NONE}"

    def short(self, league: lol.league.SummonerLeagueEntryData) -> str:
        if league:
            return f"{FS.Emotes.Lol.Tier.get(league.tier)}{FS.Emotes.Lol.Rank.get(league.rank)}"
        return f"{FS.Emotes.Lol.Tier.get('UNRANKED')}{FS.Emotes.Lol.Rank.NONE}"

    @property
    def field(self) -> dict:
        value = ""
        if self.solo:
            value += f"> **Solo/Duo :** {self.league_to_line(self.solo)}"
            if self.flex:
                value += "\n"
        if self.flex:
            value += f"> **Flex :** {self.league_to_line(self.flex)}"
        if value == "":
            value = f"{FS.Emotes.Lol.Tier.get('UNRANKED')} Unranked"
        return {"name": f"{FS.Emotes.Lol.Tier.NONE} **RANKED**", "value": value, "inline": True}


class ChampionMasteries(lol.ChampionMasteries):
    class Meta(lol.ChampionMasteries.Meta):
        pass

    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)

    ###########################

    def champion_by_name(self, name: str) -> lol.ChampionMastery:
        return next((mastery for mastery in self.masteries if mastery.champion.name == name))

    def top(self, n: int = 3) -> List[lol.ChampionMastery]:
        self.masteries.sort(key=lambda m: (m.champion_level, m.champion_points), reverse=True)
        return [self.masteries[i] for i in range(min(n, len(self.masteries)))]

    def field(self, n: int = 3) -> dict:
        top = self.top(n=n)
        return {
            "name": f"{FS.Emotes.Lol.MASTERIES[0]} **MASTERIES**",
            "value": (
                "\n".join([f"> {self.champion_to_line(champ)}" for champ in top])
                if len(top) > 0
                else f"{FS.Emotes.Lol.MASTERIES[0]} *Aucune maitrise*"
            ),
            "inline": True,
        }

    @classmethod
    def champion_to_line(cls, champion: lol.ChampionMastery) -> str:
        return f"{FS.Emotes.Lol.MASTERIES[champion.champion_level]} **{FS.Emotes.Lol.Champions.get(champion.champion_id)}** *{cls.champion_points_formatted(champion)}*"

    @staticmethod
    def champion_points_formatted(champion: lol.ChampionMastery) -> str:
        num = float("{:.3g}".format(champion.champion_points))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return "{}{}".format("{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude])

    @staticmethod
    def level_to_color(level: int) -> disnake.Colour:
        if level == 1:
            return disnake.Colour.default()
        elif level == 2:
            return disnake.Colour.dark_gray()
        elif level == 3:
            return disnake.Colour.light_gray()
        elif level == 4:
            return disnake.Colour.lighter_gray()
        elif level == 5:
            return disnake.Colour.red()
        elif level == 6:
            return disnake.Colour.purple()
        elif level == 7:
            return disnake.Colour.blue()

    @async_property
    async def embeds(self) -> List[disnake.Embed]:
        sorted_champions = sorted(self.masteries, key=lambda c: (c.champion_level, c.champion_points), reverse=True)
        blocks: List[List[lol.ChampionMastery]] = [[] for _ in range(7)]
        for champion in sorted_champions:
            blocks[-champion.champion_level].append(champion)
        embeds: List[disnake.Embed] = []
        for j, block in enumerate(blocks):
            title = f"{FS.Emotes.Lol.MASTERIES[-(j+1)]} __**Mastery {7-j}**__"
            color = self.level_to_color(7 - j)
            text = ""
            for i, champion in enumerate(block):
                if i != 0 and i % 20 == 0:
                    embeds.append(FS.Embed(title=title, description=text, color=color))
                    text = ""
                    title = disnake.Embed.Empty
                text += f"{FS.Emotes.Lol.Champions.get(champion.champion_id)} *{self.champion_points_formatted(champion)}*\n"
            embeds.append(FS.Embed(title=title, description=text, color=color))
        return embeds


class ClashPlayers(lol.ClashPlayers):
    class Meta(lol.ClashPlayers.Meta):
        pass

    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)


class ClashTeam(lol.ClashTeam):

    _icon_url: str = (
        "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/clash/roster-logos/"
    )
    _opgg_url: str = "https://euw.op.gg/multi/query="

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
        return "I" * self.tier if self.tier != 4 else "IV"

    @property
    def sortedPlayers(self) -> List[lol.clash.ClashPlayerData]:
        temp: Dict[List[lol.clash.ClashPlayerData]] = {
            "TOP": [],
            "JUNGLE": [],
            "MIDDLE": [],
            "BOTTOM": [],
            "UTILITY": [],
            "FILL": [],
            "UNSELECTED": [],
        }
        for player in self.players:
            temp[player.position].append(player)
        return (
            temp["TOP"]
            + temp["JUNGLE"]
            + temp["MIDDLE"]
            + temp["BOTTOM"]
            + temp["UTILITY"]
            + temp["FILL"]
            + temp["UNSELECTED"]
        )

    @property
    def icon_url(self) -> str:
        return self._icon_url + str(self.icon_id) + "/1.png"

    @async_property
    async def opgg_url(self) -> str:
        return self._opgg_url + "".join(
            [(await p.summoner.get()).name.replace(" ", "%20") + "%2C" for p in self.players]
        )

    @async_property
    async def embed(self) -> disnake.Embed:
        description = f"Tier **{FS.Emotes.Lol.Rank.get(self.tier)}**\n\n"
        for player in self.sortedPlayers:
            summoner = await Summoner(id=player.summoner_id).get()
            league = await summoner.league_entries.get()
            description += f"> {FS.Emotes.Lol.Positions.get(player.position)}{FS.Emotes.Lol.Tier.get(league.first.tier)} {summoner.name}"
            if player.role == "CAPTAIN":
                description += f" {FS.Emotes.Lol.CAPTAIN}"
            description += "\n"
        return FS.Embed(
            author_name=f"{self.abbreviation.upper()}",
            title=f"**{self.name}**",
            description=description,
            thumbnail=self.icon_url,
            color=disnake.Colour.blue(),
        )


class ClashTournament(lol.ClashTournament):
    class Meta(lol.ClashTournament.Meta):
        pass

    @property
    def team(self) -> ClashTeam:
        return ClashTeam(id=self.team_id, platform=self.platform)


class Summoner(lol.Summoner):

    _icon_url: str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/"
    _opgg_url: str = "https://euw.op.gg/summoners/euw/"

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
        return super().current_game  # TODO

    @property
    def league_entries(self) -> "SummonerLeague":
        return SummonerLeague(summoner_id=self.id, platform=self.platform)

    ####

    @property
    def icon_url(self) -> str:
        return self._icon_url + str(self.profile_icon_id) + ".jpg"

    @property
    def opgg_url(self) -> str:
        return self._opgg_url + self.name.replace(" ", "%20")

    @async_property
    async def embed(self) -> disnake.Embed:
        championMasteries = await self.champion_masteries.get()
        summonerLeague = await self.league_entries.get()
        return FS.Embed(
            author_name=f"{self.name.upper()}",
            color=disnake.Colour.blue(),
            author_icon_url=self.icon_url,
            fields=[
                championMasteries.field(),
                summonerLeague.field,
                {"name": f"{FS.Emotes.Lol.XP} **LEVEL**", "value": f"> **{self.level}**", "inline": True},
            ],
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

    def stats_to_tuple(self, stat: lol.merakichampion.MerakiChampionStatDetailData) -> Tuple[str, str, str]:
        if stat.flat:
            if stat.per_level:
                return [
                    f"{round(stat.flat,2)}",
                    f"+*{stat.per_level}*",
                    f"{round(stat.flat+stat.per_level*18,2)}",
                ]
            else:
                return [f"{round(stat.flat,2)}", "", f"{round(stat.flat,2)}"]
        elif stat.percent:
            if stat.percent_per_level:
                return [
                    f"{round(stat.percent,2)}%",
                    f"+*{stat.percent_per_level}%*",
                    f"{round(stat.percent+stat.percent_per_level*18)}%",
                ]
            else:
                return [f"{round(stat.percent,2)}%", "", f"{stat.percent}%"]
        else:
            return ["*--*", "", "*--*"]

    def stat_to_line(self, stat: lol.merakichampion.MerakiChampionStatDetailData) -> str:
        tup = self.stats_to_tuple(stat)
        return f"**{tup[0]}**" + (f" *+ {tup[1]}/lvl (**{tup[2]}** at lvl 18)*" if tup[1] != "" else "")

    @property
    def stat_fields(self) -> List[dict]:
        return [
            {
                "name": f"➖ ➖ __**Base**__",
                "value": f"""{FS.Emotes.Lol.Stats.HEALT} ➖ **{self.stats_to_tuple(self.stats.health)[0]}** Hp
                            {FS.Emotes.Lol.Stats.HEALTREGEN} ➖ **{self.stats_to_tuple(self.stats.health_regen)[0]}** Hp/s
                            {FS.Emotes.Lol.Stats.MANA} ➖ **{self.stats_to_tuple(self.stats.mana)[0]}** Mana
                            {FS.Emotes.Lol.Stats.MANAREGEN} ➖ **{self.stats_to_tuple(self.stats.mana_regen)[0]}** Mana/s
                            {FS.Emotes.Lol.Stats.ARMOR} ➖ **{self.stats_to_tuple(self.stats.armor)[0]}** Armor
                            {FS.Emotes.Lol.Stats.MAGICRESISTE} ➖ **{self.stats_to_tuple(self.stats.magic_resistance)[0]}** Magic Resistance
                            {FS.Emotes.Lol.Stats.ATTACKDAMAGE} ➖ **{self.stats_to_tuple(self.stats.attack_damage)[0]}** Attack damage
                            {FS.Emotes.Lol.Stats.ATTACKSPEED} ➖ **{self.stats_to_tuple(self.stats.attack_speed)[0]}** Attack speed
                            {FS.Emotes.Lol.Stats.RANGE} ➖ **{self.stats_to_tuple(self.stats.attack_range)[0]}** Attack range
                            {FS.Emotes.Lol.Stats.MOVESPEED} ➖ **{self.stats_to_tuple(self.stats.movespeed)[0]}** Movement speed""",
                "inline": True,
            },
            {
                "name": f"**/**{FS.Emotes.Lol.XP}",
                "value": f"""{self.stats_to_tuple(self.stats.health)[1]}
                            {self.stats_to_tuple(self.stats.health_regen)[1]}
                            {self.stats_to_tuple(self.stats.mana)[1]}
                            {self.stats_to_tuple(self.stats.mana_regen)[1]}
                            {self.stats_to_tuple(self.stats.armor)[1]}
                            {self.stats_to_tuple(self.stats.magic_resistance)[1]}
                            {self.stats_to_tuple(self.stats.attack_damage)[1]}
                            {self.stats_to_tuple(self.stats.attack_speed)[1]}
                            {self.stats_to_tuple(self.stats.attack_range)[1]}
                            {self.stats_to_tuple(self.stats.movespeed)[1]}""",
                "inline": True,
            },
            {
                "name": f"__**18**__{FS.Emotes.Lol.XP}",
                "value": f"""**{self.stats_to_tuple(self.stats.health)[2]}** Hp
                            **{self.stats_to_tuple(self.stats.health_regen)[2]}** Hp/s
                            **{self.stats_to_tuple(self.stats.mana)[2]}** Mana
                            **{self.stats_to_tuple(self.stats.mana_regen)[2]}** Mana/s
                            **{self.stats_to_tuple(self.stats.armor)[2]}** Armor
                            **{self.stats_to_tuple(self.stats.magic_resistance)[2]}** Magic Resistance
                            **{self.stats_to_tuple(self.stats.attack_damage)[2]}** Attack damage
                            **{self.stats_to_tuple(self.stats.attack_speed)[2]}** Attack speed
                            **{self.stats_to_tuple(self.stats.attack_range)[2]}** Attack range
                            **{self.stats_to_tuple(self.stats.movespeed)[2]}** Movement speed""",
                "inline": True,
            },
        ]

    @staticmethod
    def modifiers_to_line(modifiers: List[lol.merakichampion.MerakiChampionSpellModifierData]) -> str:
        sequences: List[List[str]] = []
        end: List[str] = []
        unit: str = ""
        for modifier in modifiers:
            if len(modifier.values) > 0 and modifier.values[0] != modifier.values[-1]:
                for j, value in enumerate(modifier.values):
                    if len(sequences) <= j:
                        sequences.append([])
                    if len(modifiers) > 1:
                        sequences[j].append(f"{value}{modifier.units[j]}")
                    else:
                        sequences[j].append(f"{value}")
            else:
                end.append(f"{modifier.values[0]}{modifier.units[0]}")
            if len(modifiers) == 1:
                unit = f"{modifier.units[0]}"
        return (
            "`"
            + f"{'/'.join(' +'.join(seq) for seq in sequences)}{unit}{' +' if len(end) and len(sequences) else ''}{' +'.join(end)}".strip()
            + "`"
        )

    @staticmethod
    def spellType_to_color(abilitiy: lol.merakichampion.MerakiChampionSpellData) -> disnake.Colour:
        ret = None
        for effect in abilitiy.effects:
            if effect.description.split(":")[0].endswith("Active") or effect.description.split(":")[0].startswith(
                "Active"
            ):
                return disnake.Colour.dark_red()
            elif effect.description.split(":")[0].endswith("Passive") or effect.description.split(":")[0].startswith(
                "Passive"
            ):
                ret = disnake.Colour.dark_blue()
            elif (
                effect.description.split(":")[0].endswith("Innate")
                or effect.description.split(":")[0].startswith("Innate")
            ) and ret == None:
                ret = disnake.Colour.dark_purple()
        return ret

    def ability_detailled_embed(self, letter: str) -> List[disnake.Embed]:
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

        embeds: List[disnake.Embed] = []

        for ability in abilities:
            embed = FS.Embed(
                title=f"__**{letter.upper()} - {ability.name}**__",
                thumbnail=ability.icon,
                color=self.spellType_to_color(ability),
            )
            embed.add_field(
                name="Cost",
                value=(
                    f"{FS.Emotes.Lol.Stats.Ressource(ability.resource)} {self.modifiers_to_line(ability.cost.modifiers)}"
                    if ability.resource
                    else "`--`"
                ),
            )
            text = (
                f"{FS.Emotes.Lol.Stats.ABILITYHASTE} {self.modifiers_to_line(ability.cooldown.modifiers)}"
                if ability.cooldown
                else "`--`"
            )
            try:
                text += f"{ability.recharge_rate}" if ability.recharge_rate else ""
            except (RuntimeError, AttributeError):
                pass
            embed.add_field(
                name="Cooldown",
                value=text,
            )  # TODO Add minition recharge ?
            embed.add_field(
                name="Range",
                value=f"{FS.Emotes.Lol.TargetType.get(ability.targeting)} `{ability.target_range}`"
                if ability.target_range
                else (
                    f"{FS.Emotes.Lol.TargetType.get(ability.targeting)} `{ability.effect_radius}`"
                    if ability.effect_radius
                    else "`--`"
                ),
            )  # TODO Add zone type ?
            for effect in ability.effects:
                description = "> " + "\n> ".join(effect.description.split("\n"))
                for attr in effect.leveling:
                    description += f"\n\n**{attr.attribute} :**\n"
                    if attr.modifiers and len(attr.modifiers) > 0:
                        description += f"{self.modifiers_to_line(attr.modifiers)}"
                embed.add_field(name="➖", value=description, inline=False)

            details: List[str] = []
            if ability.on_target_cd_static and ability.on_target_cd_static.lower() != "none":
                details.append(
                    f"> **Per target cd:** {FS.Emotes.Lol.Stats.ABILITYHASTE} `{ability.on_target_cd_static}`"
                )
            if ability.targeting and ability.targeting.lower() != "none":
                details.append(f"> **Target type:** `{ability.targeting}`")
            if ability.spell_effects and ability.spell_effects.lower() != "none":
                details.append(f"> **Effect type:** `{ability.spell_effects}`")
            if ability.width and ability.width.lower() != "none":
                details.append(f"> **Width:** `{ability.width}`")
            if ability.effect_radius and ability.effect_radius.lower() != "none":
                details.append(f"> **Effect Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.effect_radius}`")
            if ability.tether_radius and ability.tether_radius.lower() != "none":
                details.append(f"> **Tether Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.tether_radius}`")
            if ability.inner_radius and ability.inner_radius.lower() != "none":
                details.append(f"> **Inner Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.inner_radius}`")
            if ability.collision_radius and ability.collision_radius.lower() != "none":
                details.append(f"> **Collision Radius:** {FS.Emotes.Lol.Stats.RANGE} `{ability.collision_radius}`")
            if ability.damage_type and ability.damage_type.lower() != "none":
                details.append(f"> **Damage type:** `{ability.damage_type}`")
            if ability.affects and ability.affects.lower() != "none":
                details.append(f"> **Affects:** `{ability.affects}`")
            if ability.spellshieldable and ability.spellshieldable.lower() != "none":
                details.append(f"> **Spellshieldable:** `{ability.spellshieldable}`")
            if ability.projectile and ability.projectile.lower() != "none":
                details.append(f"> **Projectile:** `{ability.projectile}`")
            if ability.missile_speed and ability.missile_speed.lower() != "none":
                details.append(f"> **Missile speed:** `{ability.missile_speed}`")
            if ability.on_hit_effects and ability.on_hit_effects.lower() != "none":
                details.append(f"> **On hit effects:** `{ability.on_hit_effects}`")
            if ability.occurrence and ability.occurrence.lower() != "none":
                details.append(f"> **Occurence:** `{ability.occurrence}`")
            if ability.cast_time and ability.cast_time.lower() != "none":
                details.append(f"> **Cast time:** `{ability.cast_time}`")
            if len(details):
                embed.add_field(name="**__DETAILS__**", value="\n".join(details[: ceil(len(details) / 2)]))
                if len(details) > 1:
                    embed.add_field(name="➖", value="\n".join(details[ceil(len(details) / 2) :]))

            embeds.append(embed)
        return embeds

    def ability_embed(self, letter: str, ability: lol.merakichampion.MerakiChampionSpellData) -> disnake.Embed:
        return FS.Embed(
            title=f"__**{letter.upper()} - {ability.name}**__",
            description="\n➖\n".join(
                [
                    "> " + "\n> ".join(effect.description.split("\n"))
                    for effect in ability.effects
                    if (
                        effect.description.split(":")[0].endswith("Innate")
                        or effect.description.split(":")[0].startswith("Innate")
                        or effect.description.split(":")[0].endswith("Active")
                        or effect.description.split(":")[0].startswith("Active")
                        or effect.description.split(":")[0].endswith("Passive")
                        or effect.description.split(":")[0].startswith("Passive")
                    )
                ]
            ),
            thumbnail=ability.icon,
            color=self.spellType_to_color(ability),
        )

    @property
    def abilities_embeds(self) -> List[disnake.Embed]:
        return (
            [self.ability_embed("p", p) for p in self.abilities.p]
            + [self.ability_embed("q", q) for q in self.abilities.q]
            + [self.ability_embed("w", w) for w in self.abilities.w]
            + [self.ability_embed("e", e) for e in self.abilities.e]
            + [self.ability_embed("r", r) for r in self.abilities.r]
        )

    @property
    def stats_embed(self) -> List[disnake.Embed]:
        embed = FS.Embed(
            title="__**STATS**__",
            description=f"{FS.Emotes.Lol.AttackType.get(self.adaptive_type.split('_')[0])} {FS.Emotes.Lol.AttackType.get(self.attack_type)} "
            + " ".join([f"{FS.Emotes.Lol.Roles.get(role)}" for role in self.roles]),
            color=disnake.Colour.dark_blue(),
        )
        for field in self.stat_fields:
            embed.add_field(name=field.get("name"), value=field.get("value"), inline=field.get("inline", True))
        embed.add_field(name="➖", value="➖", inline=False)
        stats: List[str] = []
        if self.stats.acquisition_radius:
            stats.append(f"**Acquisition radius:** `{round(self.stats.acquisition_radius.flat,3)}`")
        if self.stats.selection_radius:
            stats.append(f"**Selection radius:** `{round(self.stats.selection_radius.flat,3)}`")
        if self.stats.pathing_radius:
            stats.append(f"**Pathing radius:** `{round(self.stats.pathing_radius.flat,3)}`")
        if self.stats.gameplay_radius:
            stats.append(f"**Gameplay radius:** `{round(self.stats.gameplay_radius.flat,3)}`")
        if self.stats.attack_speed_ratio:
            stats.append(f"**attack speed ratio:** `{round(self.stats.attack_speed_ratio.flat,3)}`")
        if self.stats.attack_cast_time:
            stats.append(f"**attack cast time:** `{round(self.stats.attack_cast_time.flat,3)}`")
        if self.stats.attack_speed_ratio:
            stats.append(f"**attack speed ratio:** `{round(self.stats.attack_speed_ratio.flat,3)}`")
        if self.stats.attack_total_time:
            stats.append(f"**attack total time:** `{round(self.stats.attack_total_time.flat,3)}`")
        if self.stats.attack_delay_offset:
            stats.append(f"**attack delay offset:** `{round(self.stats.attack_delay_offset.flat,3)}`")
        if stats:
            embed.add_field(name="**ADVANCED**", value="\n".join(stats))
        stats: List[str] = []
        if self.stats.aram_damage_taken and self.stats.aram_damage_taken.flat != 1.0:
            stats.append(f"**Damage taken:** `{round((1-self.stats.aram_damage_taken.flat)*100,2)}%`")
        if self.stats.aram_damage_dealt and self.stats.aram_damage_dealt.flat != 1.0:
            stats.append(f"**Damage dealt:** `{round((1-self.stats.aram_damage_dealt.flat)*100,2)}%`")
        if self.stats.aram_healing and self.stats.aram_healing.flat != 1.0:
            stats.append(f"**Healing:** `{round((1-self.stats.aram_healing.flat)*100,2)}%`")
        if self.stats.aram_shielding and self.stats.aram_shielding.flat != 1.0:
            stats.append(f"**Shield:** `{round((1-self.stats.aram_shielding.flat)*100,2)}%`")
        if stats:
            embed.add_field(name="**ARAM**", value="\n".join(stats))
        stats: List[str] = []
        if self.stats.urf_damage_taken and self.stats.urf_damage_taken.flat != 1.0:
            stats.append(f"**Damage taken:** `{round((1-self.stats.urf_damage_taken.flat)*100,2)}%`")
        if self.stats.urf_damage_dealt and self.stats.urf_damage_dealt.flat != 1.0:
            stats.append(f"**Damage dealt:** `{round((1-self.stats.urf_damage_dealt.flat)*100,2)}%`")
        if self.stats.urf_healing and self.stats.urf_healing.flat != 1.0:
            stats.append(f"**Healing:** `{round((1-self.stats.urf_healing.flat)*100,2)}%`")
        if self.stats.urf_shielding and self.stats.urf_shielding.flat != 1.0:
            stats.append(f"**Shield:** `{round((1-self.stats.urf_shielding.flat)*100,2)}%`")
        if stats:
            embed.add_field(name="**URF**", value="\n".join(stats))
        if embed.fields:
            return [self.BaseEmbed, embed]
        return [self.BaseEmbed]

    @property
    def BaseEmbed(self) -> disnake.Embed:
        embed = FS.Embed(
            author_name=self.full_name if self.full_name else self.name,
            title=f"*{self.title}*",
            description=f'> "{self.lore[:200]}[...]"' if len(self.lore) > 200 else f'> "{self.lore}"',
            author_icon_url=self.skins[0].tile_path,
            color=disnake.Colour.dark_blue(),
            thumbnail=self.skins[0].load_screen_path,
            footer_text=f"Last changed in patch {self.patch_last_changed}",
        )
        return embed

    @property
    def embeds(self) -> List[disnake.Embed]:
        embeds = [self.BaseEmbed]
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

    @property
    def emote(self) -> str:
        return FS.Emotes.Lol.Champions.get(self.id)


class CurrentGame(lol.spectator.CurrentGame):
    class Meta(lol.spectator.CurrentGame.Meta):
        pass

    @property
    def summoner(self) -> "Summoner":
        return Summoner(id=self.summoner_id, platform=self.platform)

    ######

    @property
    def map_name(self) -> str:
        map_name = next(
            (mapData.get("mapName") for mapData in mapsData if mapData.get("mapId") == self.map_id), "UNKNOWN"
        )
        if map_name == "UNKNOWN":
            logging.warning(f"No map matching id {self.map_id}")
        return map_name

    @property
    def game_name(self) -> str:
        game_name = next(
            (queueData.get("description") for queueData in queuesData if queueData.get("queueId") == self.queue_id),
            "UNKNOWN------",
        )[:-6]
        if game_name == "UNKNOWN":
            logging.warning(f"Game name not found for {self.queue_id}")
        return game_name

    @property
    def map_image(self) -> str:
        if self.map_name == "Summoner's Rift":
            return FS.Images.Lol.RIFT
        elif self.map_name == "Howling Abyss":
            return FS.Images.Lol.ARAM
        else:
            logging.info(f"Map image not found for the {self.map_name = }")
            return disnake.Embed.Empty

    @property
    def configEmbed(self) -> disnake.Embed:
        return FS.Embed(
            title=f"{FS.Emotes.Lol.LOGO} __**GAME EN COURS**__",
            description=f"> **Map :** `{self.map_name}`\n> **Type :** `{self.game_name}`\n> **Durée :** `{strftime('%M:%S', gmtime(self.length_secs))}`",
            color=disnake.Colour.blue(),
            thumbnail=self.map_image,
        )

    @async_property
    async def team_fields(self) -> List[dict]:
        ret: List[dict] = []
        for j, team in enumerate(self.teams):
            participant_tuples = [await self.participant_lines(p) for p in team.participants]
            for i in range(len(participant_tuples[0])):
                ret.append(
                    {
                        "name": (f"__**TEAM**__ {FS.Emotes.ALPHA[j]}" if not i else "➖"),
                        "value": "\n".join([p[i] for p in participant_tuples]),
                        "inline": True,
                    }
                )
        return ret

    async def participant_lines(self, participant: lol.spectator.CurrentGameParticipantData) -> Tuple[str, str, str]:
        league: SummonerLeague = await SummonerLeague(summoner_id=participant.summoner_id).get()
        championMastery: lol.ChampionMastery = await lol.ChampionMastery(
            summoner_id=participant.summoner_id, champion_id=participant.champion_id
        ).get()
        return (
            f"{league.short(league.first) if league else FS.Emotes.Lol.Tier.UNRANKED+FS.Emotes.Lol.Rank.NONE} **{participant.summoner_name}**",
            f"{FS.Emotes.Lol.Champions.get(participant.champion_id)} {FS.Emotes.Lol.MASTERIES[championMastery.champion_level]} ➖ {FS.Emotes.Lol.Runes.Perks.Get(participant.rune_ids[0])}{FS.Emotes.Lol.Runes.Styles.Get(participant.rune_sub_style)}",
            f"➖ {FS.Emotes.Lol.SummonerSpells.get(participant.spell_ids[0])}{FS.Emotes.Lol.SummonerSpells.get(participant.spell_ids[1])}",
        )

    def perks_field(self, perksId: List[int]) -> dict:
        return {
            "name": f"{FS.Emotes.Lol.Runes.Perks.NONE} **RUNES**",
            "value": f"""> {FS.Emotes.Lol.Runes.Perks.Get(perksId[0])}{FS.Emotes.Lol.Runes.Perks.Get(perksId[4])}{FS.Emotes.Lol.Runes.Perks.Get(perksId[6])}
        > {FS.Emotes.Lol.Runes.Perks.Get(perksId[1])}{FS.Emotes.Lol.Runes.Perks.Get(perksId[5])}{FS.Emotes.Lol.Runes.Perks.Get(perksId[7])}
        > {FS.Emotes.Lol.Runes.Perks.Get(perksId[2])}⬛{FS.Emotes.Lol.Runes.Perks.Get(perksId[8])}
        > {FS.Emotes.Lol.Runes.Perks.Get(perksId[3])}""",
            "inline": True,
        }

    def spells_field(self, spellsId: List[int]) -> dict:
        return {
            "name": f"{FS.Emotes.FLAME} **SPELL**",
            "value": f"> {FS.Emotes.Lol.SummonerSpells.get(spellsId[0])}{FS.Emotes.Lol.SummonerSpells.get(spellsId[1])}",
            "inline": True,
        }

    async def participant_embed(self, participant: lol.spectator.CurrentGameParticipantData) -> disnake.Embed:
        embed = await (await Summoner(id=participant.summoner_id).get()).embed
        champion = await MerakiChampion(id=participant.champion_id).get()
        championMastery = await lol.ChampionMastery(
            summoner_id=participant.summoner_id, champion_id=participant.champion_id
        ).get()
        embed.set_thumbnail(url=champion.skins[0].tile_path)
        masteryField: dict = {
            "name": f"{FS.Emotes.Lol.MASTERIES[0]} **MASTERY**",
            "value": f"> {ChampionMasteries.champion_to_line(championMastery)}",
            "inline": True,
        }
        for field in [self.perks_field(participant.rune_ids), self.spells_field(participant.spell_ids), masteryField]:
            embed.add_field(name=field.get("name"), value=field.get("value"))

        return embed
