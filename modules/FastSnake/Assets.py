# -*- coding: utf-8 -*-
from typing import List
from typing import Optional
from typing import Union


class Emotes:
    __rank: List[str] = [
        "\U0001f947",
        "\U0001f948",
        "\U0001f949",
        "4\u20e3",
        "5\u20e3",
        "6\u20e3",
        "7\u20e3",
        "8\u20e3",
        "9\u20e3",
        "\U0001f51f",
        "\U0001f1e6",
        "\U0001f1e7",
        "\U0001f1e8",
        "\U0001f1e9",
        "\U0001f1ea",
    ]
    __num: List[str] = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    ALPHA: List[str] = [
        "\U0001f1e6",
        "\U0001f1e7",
        "\U0001f1e8",
        "\U0001f1e9",
        "\U0001f1ea",
        "\U0001f1eb",
        "\U0001f1ec",
        "\U0001f1ed",
    ]

    class CardColor:
        COEUR: str = ":hearts:"
        PIQUE: str = ":spade:"
        CARREAU: str = ":diamonds:"
        TREFLE: str = ":clubs:"

    POROSNACK: str = "<:porosnack:908477364135161877>"
    BOUDHAPOG: str = "<:BoudhaPog:854084071055032340>"
    RESTART: str = "<:restart:1009104340524478534"

    BRACKET: str = "<:bracketicon:1007206320908271726>"
    CROSSING_SWORD_BLUE: str = "<:Role_Moderator:1009104341732433930>"
    CROSSING_SWORD_WHITE: str = "<:crossing_sword_gold:1009757236626731018>"
    ROLES: str = "<:roles:1009104343057842398>"
    UTILITY_WHEEL: str = "<:utility:1009104344286761050>"
    GEMME_ANIMED: str = "<a:utility_boosting:1009104346534924309>"
    GEMME: str = "<:utilityboost:1009104353375830088>"
    ARROWS_DOWN: str = "<a:utility_bottompage:1009104348296519690>"
    ARROWS_UP: str = "<a:utility_toppage:1009104349798084759>"
    LOADING: str = "<a:utility6:1009104352239161404>"
    BOOK_PURPLE: str = "<:AcePurpleRoles:1009104397147582515>"
    TWITCH: str = "<:twitch:1009104398091292735>"
    TARGET_BLUE: str = "<:targetblue:1009110751404892211>"
    TARGERT_GOLD: str = "<:target:1009110752721899540>"
    ADD_FRIEND: str = "<:addfriend:1009757240397402133>"
    SPECTATOR: str = "<:spectator:1009809802995712010>"
    FLAME: str = "<:eternal:1009809808955809803>"
    BAN: str = "<:ban:1009809814563594281>"

    class Lol:

        LOGO: str = "<:lol:1007993779984277606>"
        CRIT: str = "<:crit:1009767528395972708>"
        RIOTFIST: str = "<:rp:1009110720559984661>"
        OPGG: str = "<:opgg:1007995866092671006>"
        CHEST: str = "<:chest:1007206306693795930>"
        CHESTACQUIRED: str = "<:chestacquired:1007206299664125952>"
        CAPTAIN: str = "<:captain:1007206303992643624>"
        NASHOR: str = "<:nashor:1009110717967904798>"
        HERALD: str = "<:herald:1009110739665043457>"
        TURRET: str = "<:turret:1009760393201201183>"
        GOLD: str = "<:gold:1009759450514587649>"
        CS: str = "<:cs:1009757238254120983>"
        RIFT: str = "<:rift:1007278042923671623>"
        ARAM: str = "<:aram:1007278045402517604>"
        WHEEL: str = "<:wheel:1012810451219910786>"

        class AttackType:
            MELEE: str = "<:melee:1012810452956348486>"
            RANGE: str = "<:range:1012810455015751710>"
            ABILITYPOWER: str = "<:abilitypower:1010137865545592912>"
            ATTACKDAMAGE: str = "<:attackdamage:1010137867256873040>"

            @classmethod
            def get(cls, key: str):
                if key == "MELEE":
                    return cls.MELEE
                elif key == "PHYSICAL":
                    return cls.ATTACKDAMAGE
                elif key == "RANGED":
                    return cls.RANGE
                elif key == "MAGIC":
                    return cls.ABILITYPOWER

        TROPHIES: List[str] = [
            "<:trophy:1007206322669879326>",
            "<:trophy4:1009763643312853063>",
            "<:trophy8:1009763639705751643>",
            "<:trophy16:1009763637499531264>",
        ]

        class TargetType:

            DIRECTION: str = "<:Missile:1012032303733674014>"
            AOE: str = "<:Aoe:1012032302240501803>"
            LOCATION: str = "<:Location:1012032299698753607>"
            UNIT: str = "<:targetblue:1009110751404892211>"
            SELF: str = "<:selftarget:1012034302176931912>"

            @classmethod
            def get(cls, key: str):
                if key in ["Unit", "Auto", "Varied", "Unit / Location", "Unit / Auto"]:
                    return cls.UNIT
                elif key in ["Location", "Location / Auto", "Auto / Location", "Direction / Auto / Location"]:
                    return cls.LOCATION
                elif key in ["Direction", "Direction / Auto", "Vector"]:
                    return cls.DIRECTION
                elif key in ["Passive"]:
                    return cls.SELF
                else:
                    return "TargetType:" + key

        class Honor:
            CHILL: str = "<:chill:1009759448367120405>"
            FRIENDLY: str = "<:friendly:1009759446202843186>"
            LEAF: str = "<:honorleaf:1009759443845652530>"

        MASTERIES: List[str] = [
            "<:mastery:1007206302755340318>",
            "<:mastery:1007206302755340318>",
            "<:mastery2:1007216014662049802>",
            "<:mastery3:1007216010635522118>",
            "<:mastery4:1007216016075542548>",
            "<:mastery5:1007216018067828756>",
            "<:mastery6:1007216019942690816>",
            "<:mastery7:1007216021356167189>",
        ]

        TOKENS: List[str] = [
            "<:tokennone:1009110731142221947>",
            "<:tokeniron:1009110728713707531>",
            "<:tokenbronze:1009110721415622758>",
            "<:tokensilver:1009110734170509422>",
            "<:tokengold:1009110726222286898>",
            "<:tokenplatinum:1009110732887048272>",
            "<:tokendiamond:1009110724313890897>",
            "<:tokenmaster:1009110730345304205>",
            "<:tokengrandmaster:1009110727358939248>",
            "<:tokenchallenger:1009110722657132615>",
        ]

        class Runes:
            class Styles:
                NONE: str = "<:rune:1007206351019180042>"
                DOMINATION: str = "<:runedomination:1007206360640925737>"
                PRECISION: str = "<:runeprecision:1007206358950621225>"
                RESOLVE: str = "<:runeresolve:1007206352252309614>"
                SORCERY: str = "<:runesorcery:1007206355867811921>"
                INSPIRATION: str = "<:runewhimsy:1007206353577721886>"

                @classmethod
                def Get(cls, id: int) -> str:
                    if id == 8000:
                        return cls.PRECISION
                    elif id == 8100:
                        return cls.DOMINATION
                    elif id == 8200:
                        return cls.SORCERY
                    elif id == 8300:
                        return cls.INSPIRATION
                    elif id == 8400:
                        return cls.RESOLVE
                    else:
                        return cls.NONE

            class Perks:
                NONE: str = "<:rune:1007206351019180042>"

                AERY: str = " <:summonaery:1009809715464777848>"
                PHASERUSH: str = "<:phaserush:1009809718031696073>"
                COMET: str = "<:arcanecomet:1009809720699273226>"
                GRASP: str = "<:graspoftheundying:1009809724650311700>"
                AFTERSHOCK: str = "<:veteranaftershock:1009809726743269387>"
                GUARDIAN: str = "<:guardian:1009809730161610752>"
                PRESSTHEATACK: str = "<:presstheattack:1009809735358357516>"
                LETALTEMPO: str = "<:lethaltempotemp:1009809745688924160>"
                FLEETFOOTWORK: str = "<:fleetfootwork:1009809752349491250>"
                CONQUEROR: str = "<:conqueror:1009809758183755888>"
                ELECTROCUTE: str = "<:electrocute:1009809766752735345>"
                DARKHARVEST: str = "<:darkharvest:1009809771060269187>"
                PREDATOR: str = "<:predator:1009809778920390677>"
                HAILOFBLADES: str = "<:hailofblades:1009889839891632209>"
                FIRSSTRIKE: str = "<:firststrike:1009889837999984650>"
                GLACIALAUGMENT: str = "<:glacialaugment:1009809763716042803>"
                SPELLBOOK: str = "<:unsealedspellbook:1009889842114601030>"

                RELENTLESSHUNTER: str = "<:relentlesshunter:1009981249873526835>"
                INGENIOUSHUNTER: str = "<:ingenioushunter:1009981251450568775>"
                GHOSTPORO: str = "<:ghostporo:1009981255011540992>"
                EYEBALLCOLLECTION: str = "<:eyeballcollection:1009981256420839484>"
                CHEAPSHOT: str = "<:cheapshot:1009981257947545620>"
                BISCUITDELIVERY: str = "<:biscuitdelivery:1009981361475567707>"
                COSMICINSIGHT: str = "<:cosmicinsight:1009981364214431865>"
                FUTURESMARKET: str = "<:futuresmarket:1009981365363691610>"
                HEXTECHFLASH: str = "<:hextechflashtraption:1009981366500347934>"
                MAGICALFOOTWEAR: str = "<:magicalfootwear:1009981367431467070>"
                MINIONDEMATERIALIZER: str = "<:miniondematerializer:1009981369000140852>"
                PERFECTTIMING: str = "<:perfecttiming:1009981370128404541>"
                TIMEWARPTONIC: str = "<:timewarptonic:1009981371554484304>"
                COUPDEGRACE: str = "<:coupdegrace:1009981372640796772>"
                CUTDOWN: str = "<:cutdown:1009981373773250670>"
                LEGENDALACRITY: str = "<:legendalacrity:1009981374863781938>"
                LEGENDBLOODLINE: str = "<:legendbloodline:1009981375920734319>"
                LEGENDTENACITE: str = "<:legendtenacity:1009986745393221682>"
                PRESENCEOFMIND: str = "<:presenceofmind:1009981376881238067>"
                APPROACHVELOCITY: str = "<:approachvelocity:1009981378374414377>"
                WATERWALKING: str = "<:waterwalking:1009981379171324015>"
                UNFLINCHING: str = "<:unflinching:1009981380479942686>"
                TRANSCENDENCE: str = "<:transcendence:1009981381583048824>"
                SCORCH: str = "<:scorch:1009981383004934184>"
                POKESHIELD: str = "<:pokeshield:1009981384502288424>"
                NIMBUSCLOAK: str = "<:nimbuscloack:1009981385668304896>"
                MANAFLOWBAND: str = "<:manaflowband:1009981387090178149>"
                LASTSTAND: str = "<:laststand:1009981388180705372>"
                GATHERINGSTORM: str = "<:gatheringstorm:1009981389267021824>"
                CELERITYTEMP: str = "<:celeritytemp:1009981390357540925>"
                ABSOLUTEFOCUS: str = "<:absolutefocus:1009981391741661284>"
                SECONDWIND: str = "<:secondwind:1009981392916054026>"
                REVITALIZE: str = "<:revitalize:1009981394342137977>"
                OVERGROWTH: str = "<:overgrowth:1009981395914989689>"
                SHIELDBASH: str = "<:mirrorshell:1009981397529800754>"
                FONTOFLIFE: str = "<:fontoflife:1009981400432267304>"
                DEMOLISH: str = "<:demolish:1009981401942216824>"
                CONDITIONING: str = "<:conditioning:1009981403015954583>"
                BONEPLATING: str = "<:boneplating:1009981405452828738>"
                ZOMBIEWARD: str = "<:zombieward:1009981407373824030>"
                ULTIMATEHUNTER: str = "<:ultimatehunter:1009981408216887367>"
                TREASUREHUNTER: str = "<:treasurehunter:1009981409638744095>"
                TASTEOFBLOOD: str = "<:tasteofblood:1009981411127742484>"
                SUDDENIMPACT: str = "<:suddenimpact:1009981412432171038>"
                TRIUMPHE: str = "<:triumph:1009985534732554341>"
                OVERHEALT: str = "<:overheal:1009985535709810729>"

                MAGICRESIST: str = "<:magicresistance:1009809784586903552>"
                HEALT: str = "<:healt:1009809788194013334>"
                ABILITYHASTE: str = "<:abilityhaste:1009809789930446928>"
                ATTACKSPEED: str = "<:attackspeed:1009809793369788427>"
                ARMOR: str = "<:armor:1009809797614407690>"
                ABILITYPOWER: str = "<:abilityPower:1009809800579780608>"

                @classmethod
                def Get(cls, id: int) -> str:
                    if id == 5001:
                        return cls.HEALT
                    elif id == 5002:
                        return cls.ARMOR
                    elif id == 5003:
                        return cls.MAGICRESIST
                    elif id == 5005:
                        return cls.ATTACKSPEED
                    elif id == 5007:
                        return cls.ABILITYHASTE
                    elif id == 5008:
                        return cls.ABILITYPOWER
                    elif id == 5008:
                        return cls.ABILITYPOWER

                    elif id == 8005:
                        return cls.PRESSTHEATACK
                    elif id == 8008:
                        return cls.LETALTEMPO
                    elif id == 8009:
                        return cls.PRESENCEOFMIND
                    elif id == 8010:
                        return cls.CONQUEROR
                    elif id == 8014:
                        return cls.COUPDEGRACE
                    elif id == 8017:
                        return cls.CUTDOWN
                    elif id == 8021:
                        return cls.FLEETFOOTWORK
                    elif id == 8105:
                        return cls.RELENTLESSHUNTER
                    elif id == 8106:
                        return cls.ULTIMATEHUNTER
                    elif id == 8112:
                        return cls.ELECTROCUTE
                    elif id == 8120:
                        return cls.GHOSTPORO
                    elif id == 8124:
                        return cls.PREDATOR
                    elif id == 8126:
                        return cls.CHEAPSHOT
                    elif id == 8128:
                        return cls.DARKHARVEST
                    elif id == 8134:
                        return cls.INGENIOUSHUNTER
                    elif id == 8135:
                        return cls.TREASUREHUNTER
                    elif id == 8136:
                        return cls.ZOMBIEWARD
                    elif id == 8138:
                        return cls.EYEBALLCOLLECTION
                    elif id == 8139:
                        return cls.TASTEOFBLOOD
                    elif id == 8143:
                        return cls.SUDDENIMPACT
                    elif id == 8210:
                        return cls.TRANSCENDENCE
                    elif id == 8214:
                        return cls.AERY
                    elif id == 8224:
                        return cls.POKESHIELD
                    elif id == 8226:
                        return cls.MANAFLOWBAND
                    elif id == 8229:
                        return cls.COMET
                    elif id == 8230:
                        return cls.PHASERUSH
                    elif id == 8232:
                        return cls.WATERWALKING
                    elif id == 8233:
                        return cls.ABSOLUTEFOCUS
                    elif id == 8234:
                        return cls.CELERITYTEMP
                    elif id == 8236:
                        return cls.GATHERINGSTORM
                    elif id == 8237:
                        return cls.SCORCH
                    elif id == 8242:
                        return cls.UNFLINCHING
                    elif id == 8275:
                        return cls.NIMBUSCLOAK
                    elif id == 8299:
                        return cls.LASTSTAND
                    elif id == 8304:
                        return cls.MAGICALFOOTWEAR
                    elif id == 8306:
                        return cls.HEXTECHFLASH
                    elif id == 8313:
                        return cls.PERFECTTIMING
                    elif id == 8316:
                        return cls.MINIONDEMATERIALIZER
                    elif id == 8321:
                        return cls.FUTURESMARKET
                    elif id == 8345:
                        return cls.BISCUITDELIVERY
                    elif id == 8347:
                        return cls.COSMICINSIGHT
                    elif id == 8351:
                        return cls.GLACIALAUGMENT
                    elif id == 8360:
                        return cls.SPELLBOOK
                    elif id == 8369:
                        return cls.FIRSSTRIKE
                    elif id == 8401:
                        return cls.SHIELDBASH
                    elif id == 8410:
                        return cls.APPROACHVELOCITY
                    elif id == 8352:
                        return cls.TIMEWARPTONIC
                    elif id == 8429:
                        return cls.CONDITIONING
                    elif id == 8437:
                        return cls.GRASP
                    elif id == 8439:
                        return cls.AFTERSHOCK
                    elif id == 8444:
                        return cls.SECONDWIND
                    elif id == 8446:
                        return cls.DEMOLISH
                    elif id == 8451:
                        return cls.OVERGROWTH
                    elif id == 8453:
                        return cls.REVITALIZE
                    elif id == 8463:
                        return cls.FONTOFLIFE
                    elif id == 8465:
                        return cls.GUARDIAN
                    elif id == 8473:
                        return cls.BONEPLATING
                    elif id == 9101:
                        return cls.OVERHEALT
                    elif id == 9103:
                        return cls.LEGENDBLOODLINE
                    elif id == 9104:
                        return cls.LEGENDALACRITY
                    elif id == 9105:
                        return cls.LEGENDTENACITE
                    elif id == 9111:
                        return cls.TRIUMPHE
                    elif id == 9923:
                        return cls.HAILOFBLADES
                    return f"Perks:{id}"

        class Positions:
            UNSELECTED: str = "<:unselected:1007994502318923896>"
            TOP: str = "<:top:1007994503858245672>"
            JUNGLE: str = "<:jungle:1007994500066574407>"
            MIDDLE: str = "<:mid:1007994497810059304>"
            BOTTOM: str = "<:bot:1007994496245579916>"
            UTILITY: str = "<:support:1007994494744002631>"
            FILL: str = "<:fill:1007994493250850897>"

            @classmethod
            def get(cls, key: str) -> Optional[str]:
                if key == "UNSELECTED":
                    return cls.UNSELECTED
                elif key == "TOP":
                    return cls.TOP
                elif key == "JUNGLE":
                    return cls.JUNGLE
                elif key == "MIDDLE":
                    return cls.MIDDLE
                elif key == "BOTTOM":
                    return cls.BOTTOM
                elif key == "UTILITY":
                    return cls.UTILITY
                elif key == "FILL":
                    return cls.FILL
                else:
                    return None

        class Roles:
            ADC: str = "<:adc:1009110682639290380>"
            ASSASSIN: str = "<:assassin:1009110684023410698>"
            FIGHTER: str = "<:figher:1009110714327257098>"
            MAGE: str = "<:mage:1009110736691282061>"
            SUPPORT: str = "<:support:1009110748523413556>"
            TANK: str = "<:tank:1009110749727162401>"

            @classmethod
            def get(cls, id: str):
                if id == "FIGHTER":
                    return cls.FIGHTER
                elif id == "TANK":
                    return cls.TANK
                elif id == "ASSASSIN":
                    return cls.ASSASSIN
                elif id == "MARKSMAN":
                    return cls.ADC
                elif id == "MAGE":
                    return cls.MAGE
                elif id == "SUPPORT":
                    return cls.SUPPORT
                else:
                    return ""

        class Drakes:
            CHEMTECH: str = "<:chemtechdrake:1009110685256515705>"
            CLOUD: str = "<:clouddrake:1009110688876212314>"
            ELDER: str = "<:elderdrake:1009110711957471392>"
            HEXTECH: str = "<:hextechdrake:1009110719196844082>"
            OCEAN: str = "<:oceandrake:1009110741393088604>"
            INFERNAL: str = "<:infernaldrake:1009110735462342656>"
            MOUNTAIN: str = "<:mountainedrake:1009110738335436810>"

        class Stats:
            RANGE: str = "<:range:1010137849632395295>"
            MOVESPEED: str = "<:movespeed:1010137850760659016>"
            TENACITE: str = "<:tenacite:1010137852534861825>"
            CRIT: str = "<:crit:1010137853856055387>"
            ABILITYHASTE: str = "<:abilityhaste:1010137855223410729>"
            LIFESTEAL: str = "<:lifesteal:1010137856301355048>"
            LIFESTEALPHYSIC: str = "<:lifestealphysic:1010137857618366486>"
            ATTACKSPEED: str = "<:attackspeed:1010137859073777694>"
            MAGICRESISTE: str = "<:magicresiste:1010137860374024284>"
            ARMOR: str = "<:armor:1010137862043357224>"
            MAGICPEN: str = "<:magicpen:1010137863234519041>"
            ARMORPEN: str = "<:armorpen:1010137864379564052>"
            ABILITYPOWER: str = "<:abilitypower:1010137865545592912>"
            ATTACKDAMAGE: str = "<:attackdamage:1010137867256873040>"
            MANAREGEN: str = "<:manaregen:1010137868615827476>"
            HEALTREGEN: str = "<:healtregen:1010137869836369960>"
            HEALT: str = "<:healt:1009809788194013334>"
            MANA: str = "💧"

            @classmethod
            def Ressource(cls, id: str):
                if id == "MANA" or id == "MANA_PER_SECOND":
                    return cls.MANA
                elif id == "GRIT":
                    return cls.ARMOR
                elif id == "OTHER":
                    return cls.MANA
                elif id == "CHARGE":
                    return cls.ABILITYPOWER
                elif id == "ENERGY":
                    return cls.MANA
                elif id == "CURRENT_HEALTH" or id == "HEALTH" or id == "MAXIMUM_HEALTH":
                    return cls.HEALT
                elif id == "FURY":
                    return cls.ARMORPEN
                else:
                    return ""

        class SummonerSpells:
            NONE: str = "<:summonerSpell:1009110747214774402>"
            CLARITY: str = "<:clarity:1009110686573539389>"
            CLEANSE: str = "<:cleanse:1009110687836012704>"
            EXHAUSTE: str = "<:exhaust:1009110713157025832>"
            GHOST: str = "<:ghost:1009110715434545233>"
            HEALT: str = "<:healt:1009110716688633916>"
            SMITE: str = "<:smite:1009110743217618974>"
            SMITE_BLUE: str = "<:smiteblue:1009110744647860394>"
            SMITE_RED: str = "<:smitered:1009110745893576835>"
            TELEPORTATION: str = "<:teleportation:1009110754051493898>"
            FLASH: str = "<:flash:1009826796981735506>"
            DASH: str = "<:dash:1009826795262054471>"
            MARK: str = "<:mark:1009826793559179304>"
            IGNITE: str = "<:ignite:1009826791856287795>"
            BARRIER: str = "<:barrier:1009826789788487680>"

            @classmethod
            def get(cls, id: int):
                if id == 1:
                    return cls.CLEANSE
                elif id == 3:
                    return cls.EXHAUSTE
                elif id == 4:
                    return cls.FLASH
                elif id == 6:
                    return cls.GHOST
                elif id == 7:
                    return cls.HEALT
                elif id == 11:
                    return cls.SMITE
                elif id == 12:
                    return cls.TELEPORTATION
                elif id == 13:
                    return cls.CLARITY
                elif id == 14:
                    return cls.IGNITE
                elif id == 21:
                    return cls.BARRIER
                elif id == 30:
                    return cls.NONE  # PoroKingDash
                elif id == 31:
                    return cls.NONE  # PoroMark
                elif id == 32:
                    return cls.MARK
                elif id == 39:
                    return cls.NONE  # UrfMark
                elif id == 54:
                    return cls.NONE  # UltBook
                elif id == 55:
                    return cls.NONE  # UtlBookSmite
                else:
                    return f"SumSpell:{id}"

        class Tier:
            NONE: str = "<:rankedemblem:1007206349509242880>"

            UNRANKED: str = "<:unranked:1007976696487608431>"
            IRON: str = "<:iron:1007976694646313032>"
            BRONZE: str = "<:bronze:1007976693165727785>"
            SILVER: str = "<:silver:1007992585664614471>"
            GOLD: str = "<:gold:1007976698182111312>"
            PLATINUM: str = "<:platinum:1007976699587207259>"
            DIAMOND: str = "<:diamond:1007976701130715146>"
            MASTER: str = "<:master:1007976691521564692> "
            GRANDMASTER: str = "<:grandmaster:1007976690078732348>"
            CHALLENGER: str = "<:challenger:1007976687948009544>"

            @classmethod
            def get(cls, key: str) -> Optional[str]:
                if key == "NONE":
                    return cls.NONE
                elif key == "UNRANKED":
                    return cls.IRON
                elif key == "IRON":
                    return cls.IRON
                elif key == "BRONZE":
                    return cls.BRONZE
                elif key == "SILVER":
                    return cls.SILVER
                elif key == "GOLD":
                    return cls.GOLD
                elif key == "PLATINUM":
                    return cls.PLATINUM
                elif key == "DIAMOND":
                    return cls.DIAMOND
                elif key == "MASTER":
                    return cls.MASTER
                elif key == "GRANDMASTER":
                    return cls.GRANDMASTER
                elif key == "CHALLENGER":
                    return cls.CHALLENGER
                else:
                    return None

        class Champions:
            NONE: str = "<:None:1009838143974944852>"

            YASUO: str = "<:Yasuo:1009837006408396850>"
            ZAC: str = "<:Zac:1009837008362934362>"
            GNAR: str = "<:Gnar:1009837010036477982>"
            SIVIR: str = "<:Sivir:1009837011869372498>"
            SERAPHINE: str = "<:Seraphine:1009837013832306710>"
            KAISA: str = "<:KaiSa:1009837015862349895>"
            ZYRA: str = "<:Zyra:1009837017783357530>"
            ZOE: str = "<:Zoe:1009837019683364884>"
            KAYN: str = "<:Kayn:1009837021914730496>"
            SION: str = "<:Sion:1009837023852515359>"
            AURELIONSOL: str = "<:AurelionSol:1009837025710579722>"
            SYNDRA: str = "<:Syndra:1009837027782578227>"
            QUINN: str = "<:Quinn:1009837029783244800>"
            DIANA: str = "<:Diana:1009837031762968706>"
            RYZE: str = "<:Ryze:1009837033985941534>"
            LISSANDRA: str = "<:Lissandra:1009837039522435132>"
            JAYCE: str = "<:Jayce:1009837049727176718>"
            DARIUS: str = "<:Darius:1009837057658585099>"
            KHAZIX: str = "<:KahZix:1009837073190092801>"
            HECARIM: str = "<:Hecarim:1009837080286867486>"
            ALISTAR: str = "<:Alistar:1009837085542334546>"
            IRELIA: str = "<:Irelia:1009837547448434829>"
            KASSADIN: str = "<:Kassadin:1009837549218439339>"
            SONA: str = "<:Sona:1009837550619349103>"
            SAMIRA: str = "<:Samira:1009837552003465309>"
            DRMUNDO: str = "<:DRMundo:1009837553442115625>"
            YUUMI: str = "<:Yummi:1009837555556040734>"
            SHACO: str = "<:Shaco:1009837557846122526>"
            ANIVIA: str = "<:Anivia:1009837559741939773>"
            RAMMUS: str = "<:Rammus:1009837561461616691>"
            AMUMU: str = "<:Amumu:1009837565827887285>"
            CHOGATH: str = "<:ChoGath:1009837567337836587>"
            KARTHUS: str = "<:Karthus:1009837570122854444>"
            GALIO: str = "<:Galio:1009837574711414784>"
            TWITCH: str = "<:Twitch:1009837579157377025>"
            EVELYNN: str = "<:Evelynn:1009837584396058704>"
            SINGED: str = "<:Singed:1009837588485505024>"
            AZIR: str = "<:Azir:1009837593237659761>"
            NAMI: str = "<:Nami:1009837595909435515>"
            AATROX: str = "<:Aatrox:1009837597574582282>"
            ZILEAN: str = "<:Zilean:1009837599562682468>"
            VI: str = "<:Vi:1009837603752779786>"
            MORGANA: str = "<:Morgana:1009837606911094845>"
            QIYANA: str = "<:Qiyana:1009837610287501342>"
            EKKO: str = "<:Ekko:1009837612388864010>"
            KLED: str = "<:Kled:1009837617933729792>"
            JAX: str = "<:Jax:1009837623197585489>"
            ZED: str = "<:Zed:1009837628826321016>"
            LUCIAN: str = "<:Lucian:1009837632836075541>"
            SENNA: str = "<:Senna:1009837638515179601>"
            VIEGO: str = "<:Viego:1009837643510591519>"
            TRYNDAMERE: str = "<:Tryndamere:1009837650569605130>"
            TAHMKENCH: str = "<:ThamKench:1009837656412278865>"
            JINX: str = "<:Jinx:1009837664196886628>"
            ZERI: str = "<:Zeri:1009837671624998995>"
            ASHE: str = "<:Ashe:1009837679875203113>"
            MISSFORTUNE: str = "<:MissFortune:1009837682651824189>"
            KINDRED: str = "<:Kindred:1009837688679055440>"
            JHIN: str = "<:Jhin:1009837698581803118>"
            BRAUM: str = "<:Braum:1009837706530017321>"
            BELVETH: str = "<:BemVeth:1009837715224797285>"
            NUNU: str = "<:Nunu:1009837721767911535>"
            OLAF: str = "<:Olaf:1009837726931112016>"
            WARWICK: str = "<:Warwick:1009837729053417482>"
            TRISTANA: str = "<:Tristana:1009837740059283486>"
            TEEMO: str = "<:Teemo:1009837744698179624>"
            AKSHAN: str = "<:Ashkan:1009837748192030800>"
            CAMILLE: str = "<:Camille:1009837753434898533>"
            TALIYAH: str = "<:Talyah:1009837756383510700>"
            VELKOZ: str = "<:VelKoz:1009837762792398899>"
            SORAKA: str = "<:Soraka:1009837772166672569>"
            JARVANIV: str = "<:Jarvan:1009838012030533782>"
            RENEKTON: str = "<:Renekton:1009838013695672330>"
            MAOKAI: str = "<:Maokai:1009838015146901596>"
            NOCTURNE: str = "<:Nocturne:1009838017051107339>"
            PYKE: str = "<:Pyke:1009838018389098536>"
            KATARINA: str = "<:Katarina:1009838020066803806>"
            MALPHITE: str = "<:malphite:1009838022096850944>"
            BLITZCRANK: str = "<:Blitzcrank:1009838023409676389>"
            RELL: str = "<:Rell:1009838024860913686>"
            DRAVEN: str = "<:Draven:1009838026970628156>"
            LULU: str = "<:Lulu:1009838028832911471>"
            ZIGGS: str = "<:Ziggs:1009838031865397378>"
            FIORA: str = "<:Fiora:1009838035690602508>"
            SEJUANI: str = "<:Sejuani:1009838038865690774>"
            VIKTOR: str = "<:Viktor:1009838042355347496>"
            NAUTILUS: str = "<:Nautlus:1009838047237505187>"
            VARUS: str = "<:Varus:1009838055143776276>"
            MASTERYI: str = "<:MasterYi:1009838058172059699>"
            RENGAR: str = "<:Rengar:1009838066279665764>"
            VOLIBEAR: str = "<:Volibear:1009838073791652021>"
            FIZZ: str = "<:Fizz:1009838080712261742>"
            GRAVES: str = "<:Graves:1009838087595110481>"
            AHRI: str = "<:Ahri:1009838095853699172>"
            SHYVANA: str = "<:Shyvana:1009838103583793182>"
            XERATH: str = "<:Xerath:1009838110957383680>"
            KAYLE: str = "<:Kayle:1009838120822386749>"
            ANNIE: str = "<:Annie:1009838133740834877>"
            APHELIOS: str = "<:Aphelios:1009838156880826368>"
            NEEKO: str = "<:Neeko:1009838166187970722>"
            SYLAS: str = "<:Sylas:1009838174241050717>"
            ORNN: str = "<:Ornn:1009838182004691024>"
            CAITLYN: str = "<:Caitlyn:1009838190447825037>"
            SWAIN: str = "<:Swain:1009838193551622315>"
            KINZHAO: str = "<:KinZhao:1009838195824918538>"
            XAYAH: str = "<:Xayah:1009838198383452231>"
            RAKAN: str = "<:Rakan:1009838203332743248>"
            TRUNDLE: str = "<:Trundle:1009838212379848774>"
            VEIGAR: str = "<:Veigar:1009838217320738916>"
            TARIC: str = "<:Taric:1009838226984403136>"
            BARD: str = "<:Bard:1009838238501982309>"
            KALISTA: str = "<:Kalista:1009838250237640754>"
            KARMA: str = "<:Karma:1009838261243494511>"
            IVERN: str = "<:Ivern:1009838272782028872>"
            REKSAI: str = "<:RekSai:1009838287977984161>"
            ILLAOI: str = "<:Illaoi:1009838299633950791>"
            CORKI: str = "<:Corki:1009838308022566923>"
            THRESH: str = "<:Tresh:1009838319703703664>"
            GANGPLANK: str = "<:GankPlank:1009838331565199391>"
            JANNA: str = "<:Janna:1009838346278817893>"
            TWISTEDFATE: str = "<:TwistedFate:1009838806083580057>"
            LUX: str = "<:Lux:1009838938527113377>"
            SHEN: str = "<:Shen:1009838939911241769>"
            KOGMAW: str = "<:KogMaw:1009838942847254628>"
            RIVEN: str = "<:Riven:1009838946148176002>"
            TALON: str = "<:Talon:1009838948027215904>"
            MALZAHAR: str = "<:Malzahar:1009838951122612335>"
            FIDDLESTICKS: str = "<:FiddleStick:1009838953249112084>"
            NILAH: str = "<:Nilah:1009838956529078394>"
            LEONA: str = "<:Leona:1009838962451431506>"
            RENATA: str = "<:Renata:1009838968130515045>"
            GWEN: str = "<:Gwen:1009838972383539271>"
            LILLIA: str = "<:lillia:1009838976951140462>"
            SETT: str = "<:Sett:1009838984148553729>"
            GAREN: str = "<:Garen:1009838990326759536>"
            KENNEN: str = "<:Kennen:1009838995322183751>"
            AKALI: str = "<:Akali:1009838997679394927>"
            YORICK: str = "<:Yorick:1009839006000873574>"
            MORDEKAISER: str = "<:Mordekaiser:1009839019271651398>"
            EZREAL: str = "<:Ezreal:1009839022123798678>"
            PANTHEON: str = "<:Pantheon:1009839023344328754>"
            VLADIMIR: str = "<:Vladimir:1009839025252741210>"
            GRAGAS: str = "<:Gragas:1009839026771066900>"
            POPPY: str = "<:Poppy:1009839029115695145>"
            YONE: str = "<:Yone:1009839030877298728>"
            UDYR: str = "<:Udyr:1009839032794087435>"
            NIDALEE: str = "<:Nidalee:1009839035306479687>"
            NASUS: str = "<:Nasus:1009839037131010169>"
            HEIMERDINGER: str = "<:HeimerDinger:1009839039106523229>"
            SKARNER: str = "<:Skarner:1009839040725536809>"
            VEX: str = "<:Vex:1009839043024003132>"
            LEBLANC: str = "<:LeBlanc:1009839045305712711>"
            CASSIOPEIA: str = "<:Cassiopeia:1009839047549653012>"
            RUMBLE: str = "<:Rumble:1009839050053660793>"
            VAYNE: str = "<:Vayne:1009839051861397524>"
            LEESIN: str = "<:LeeSin:1009839054910652446>"
            BRAND: str = "<:Brand:1009839057091706961>"
            WUKONG: str = "<:Wukong:1009839059276943441>"
            ORIANNA: str = "<:orianna:1009839078755274802>"
            ELISE: str = "<:Elise:1009839090016989194>"
            URGOT: str = "<:Urgot:1009839101983330344>"
            XINZHAO: str = "<:XinZhao:1009842143143149609>"

            @classmethod
            def get(cls, id: Union[str, int]):
                map = {
                    "266": cls.AATROX,
                    "103": cls.AHRI,
                    "84": cls.AKALI,
                    "166": cls.AKSHAN,
                    "12": cls.ALISTAR,
                    "32": cls.AMUMU,
                    "34": cls.ANIVIA,
                    "1": cls.ANNIE,
                    "523": cls.APHELIOS,
                    "22": cls.ASHE,
                    "136": cls.AURELIONSOL,
                    "268": cls.AZIR,
                    "432": cls.BARD,
                    "200": cls.BELVETH,
                    "53": cls.BLITZCRANK,
                    "63": cls.BRAND,
                    "201": cls.BRAUM,
                    "51": cls.CAITLYN,
                    "164": cls.CAMILLE,
                    "69": cls.CASSIOPEIA,
                    "31": cls.CHOGATH,
                    "42": cls.CORKI,
                    "122": cls.DARIUS,
                    "131": cls.DIANA,
                    "119": cls.DRAVEN,
                    "36": cls.DRMUNDO,
                    "245": cls.EKKO,
                    "60": cls.ELISE,
                    "28": cls.EVELYNN,
                    "81": cls.EZREAL,
                    "9": cls.FIDDLESTICKS,
                    "114": cls.FIORA,
                    "105": cls.FIZZ,
                    "3": cls.GALIO,
                    "41": cls.GANGPLANK,
                    "86": cls.GAREN,
                    "150": cls.GNAR,
                    "79": cls.GRAGAS,
                    "104": cls.GRAVES,
                    "887": cls.GWEN,
                    "120": cls.HECARIM,
                    "74": cls.HEIMERDINGER,
                    "420": cls.ILLAOI,
                    "39": cls.IRELIA,
                    "427": cls.IVERN,
                    "40": cls.JANNA,
                    "59": cls.JARVANIV,
                    "24": cls.JAX,
                    "126": cls.JAYCE,
                    "202": cls.JHIN,
                    "222": cls.JINX,
                    "145": cls.KAISA,
                    "429": cls.KALISTA,
                    "43": cls.KARMA,
                    "30": cls.KARTHUS,
                    "38": cls.KASSADIN,
                    "55": cls.KATARINA,
                    "10": cls.KAYLE,
                    "141": cls.KAYN,
                    "85": cls.KENNEN,
                    "121": cls.KHAZIX,
                    "203": cls.KINDRED,
                    "240": cls.KLED,
                    "96": cls.KOGMAW,
                    "7": cls.LEBLANC,
                    "64": cls.LEESIN,
                    "89": cls.LEONA,
                    "876": cls.LILLIA,
                    "127": cls.LISSANDRA,
                    "236": cls.LUCIAN,
                    "117": cls.LULU,
                    "99": cls.LUX,
                    "54": cls.MALPHITE,
                    "90": cls.MALZAHAR,
                    "57": cls.MAOKAI,
                    "11": cls.MASTERYI,
                    "21": cls.MISSFORTUNE,
                    "62": cls.WUKONG,
                    "82": cls.MORDEKAISER,
                    "25": cls.MORGANA,
                    "267": cls.NAMI,
                    "75": cls.NASUS,
                    "111": cls.NAUTILUS,
                    "518": cls.NEEKO,
                    "76": cls.NIDALEE,
                    "895": cls.NILAH,
                    "56": cls.NOCTURNE,
                    "20": cls.NUNU,
                    "2": cls.OLAF,
                    "61": cls.ORIANNA,
                    "516": cls.ORNN,
                    "80": cls.PANTHEON,
                    "78": cls.POPPY,
                    "555": cls.PYKE,
                    "246": cls.QIYANA,
                    "133": cls.QUINN,
                    "497": cls.RAKAN,
                    "33": cls.RAMMUS,
                    "421": cls.REKSAI,
                    "526": cls.RELL,
                    "888": cls.RENATA,
                    "58": cls.RENEKTON,
                    "107": cls.RENGAR,
                    "92": cls.RIVEN,
                    "68": cls.RUMBLE,
                    "13": cls.RYZE,
                    "360": cls.SAMIRA,
                    "113": cls.SEJUANI,
                    "235": cls.SENNA,
                    "147": cls.SERAPHINE,
                    "875": cls.SETT,
                    "35": cls.SHACO,
                    "98": cls.SHEN,
                    "102": cls.SHYVANA,
                    "27": cls.SINGED,
                    "14": cls.SION,
                    "15": cls.SIVIR,
                    "72": cls.SKARNER,
                    "37": cls.SONA,
                    "16": cls.SORAKA,
                    "50": cls.SWAIN,
                    "517": cls.SYLAS,
                    "134": cls.SYNDRA,
                    "223": cls.TAHMKENCH,
                    "163": cls.TALIYAH,
                    "91": cls.TALON,
                    "44": cls.TARIC,
                    "17": cls.TEEMO,
                    "412": cls.THRESH,
                    "18": cls.TRISTANA,
                    "48": cls.TRUNDLE,
                    "23": cls.TRYNDAMERE,
                    "4": cls.TWISTEDFATE,
                    "29": cls.TWITCH,
                    "77": cls.UDYR,
                    "6": cls.URGOT,
                    "110": cls.VARUS,
                    "67": cls.VAYNE,
                    "45": cls.VEIGAR,
                    "161": cls.VELKOZ,
                    "711": cls.VEX,
                    "254": cls.VI,
                    "234": cls.VIEGO,
                    "112": cls.VIKTOR,
                    "8": cls.VLADIMIR,
                    "106": cls.VOLIBEAR,
                    "19": cls.WARWICK,
                    "498": cls.XAYAH,
                    "101": cls.XERATH,
                    "5": cls.XINZHAO,
                    "157": cls.YASUO,
                    "777": cls.YONE,
                    "83": cls.YORICK,
                    "350": cls.YUUMI,
                    "154": cls.ZAC,
                    "238": cls.ZED,
                    "221": cls.ZERI,
                    "115": cls.ZIGGS,
                    "26": cls.ZILEAN,
                    "142": cls.ZOE,
                    "143": cls.ZYRA,
                }
                id = str(id)
                return map.get(str(id), cls.NONE)

        @classmethod
        def get(cls, position: str, rank: str) -> Optional[tuple[str, str]]:
            return (cls.Positions.get(position), cls.Tier.get(rank))

        BLUEESSENCE: str = "<:blueessence:1007206326742564895>"
        XP: str = "<:boost:1007206301144715284>"

    @classmethod
    def Num(cls, number: int, size: int = None) -> str:
        """
        Take a number and return a str of the emotes that correspond to the number.
        """
        if size and size < len(str(number)):
            raise ValueError("Argument size should be greater of equal to the lenght of the number.")

        if size != None:
            number_str = "0" * (size - len(str(number))) + str(number)
        else:
            number_str = str(number)
        return "".join([cls.__num[int(chiffre)] for chiffre in number_str])

    @classmethod
    def Ranks(cls, number: int, size: int = None) -> str:
        """
        Take a number and return a str of the emotes that correspond to the number.
        """
        if size and size < len(str(number + 1)):
            raise ValueError("Argument size should be greater of equal to the lenght of the number.")

        if size == None:
            if number == 0:
                return "🥇"
            elif number == 1:
                return "🥈"
            elif number == 2:
                return "🥉"
            elif number == 9:
                return "🔟"
            else:
                number_str = str(number + 1)
        else:
            number_str = "0" * (size - len(str(number + 1))) + str(number + 1)
        return "".join([cls.__num[int(chiffre)] for chiffre in number_str])


class Images:
    class Cards:
        COEURS: List[str] = [
            "https://i.imgur.com/sSNc54Q.png",
            "https://i.imgur.com/q4M9V3l.png",
            "https://i.imgur.com/OldvcEy.png",
            "https://i.imgur.com/wj1GoO9.png",
            "https://i.imgur.com/0B2Ud1T.png",
            "https://i.imgur.com/eCliqU4.png",
            "https://i.imgur.com/lMbRY2r.png",
            "https://i.imgur.com/cuG1fqu.png",
            "https://i.imgur.com/4NwgCla.png",
            "https://i.imgur.com/2SR4Ial.png",
        ]
        PIQUES: List[str] = [
            "https://i.imgur.com/lrkEiPh.png",
            "https://i.imgur.com/FLWt3us.png",
            "https://i.imgur.com/SlHZ8t4.png",
            "https://i.imgur.com/1mfYaX7.png",
            "https://i.imgur.com/QBHcYfF.png",
            "https://i.imgur.com/q2FfmBf.png",
            "https://i.imgur.com/Hl2Du9R.png",
            "https://i.imgur.com/QDFqD4S.png",
            "https://i.imgur.com/gU5ajry.png",
            "https://i.imgur.com/flk2YDF.png",
        ]
        CARREAUX: List[str] = [
            "https://i.imgur.com/O7cv7tN.png",
            "https://i.imgur.com/kV9fwxW.png",
            "https://i.imgur.com/VLOfZ7b.png",
            "https://i.imgur.com/tVON7pX.png",
            "https://i.imgur.com/gzzilPT.png",
            "https://i.imgur.com/1TdAJDG.png",
            "https://i.imgur.com/tdC9dvu.png",
            "https://i.imgur.com/FilOYsA.png",
            "https://i.imgur.com/pYmcUhJ.png",
            "https://i.imgur.com/hDeAMFI.png",
        ]
        TREFLES: List[str] = [
            "https://i.imgur.com/QBjfMLu.png",
            "https://i.imgur.com/EF7xnGq.png",
            "https://i.imgur.com/uQ3BIys.png",
            "https://i.imgur.com/z6nYDmr.png",
            "https://i.imgur.com/d3jR6aw.png",
            "https://i.imgur.com/xeNNQKK.png",
            "https://i.imgur.com/HXUu8pk.png",
            "https://i.imgur.com/rHgZm4v.png",
            "https://i.imgur.com/iPpeZmv.png",
            "https://i.imgur.com/idF7THF.png",
        ]
        BACK: str = "https://i.imgur.com/xAegVLz.png"

        @classmethod
        def get(cls, key: str) -> Optional[Union[List[str], str]]:
            if key == "coeur":
                return cls.Coeur
            elif key == "pique":
                return cls.PIQUES
            elif key == "carreau":
                return cls.CARREAUX
            elif key == "trefle":
                return cls.TREFLES
            elif key == "back":
                return cls.BACK
            else:
                return None

    class Poros:
        ANGRY: str = "https://i.imgur.com/bOH0XUl.png"
        BLUCH: str = "https://i.imgur.com/vliXsat.png"
        COOL: str = "https://i.imgur.com/wuPk5Fa.png"
        CRYING: str = "https://i.imgur.com/apDuJZW.png"
        TONGUELONG: str = "https://i.imgur.com/apDuJZW.png"
        TONGUESHORT: str = "https://i.imgur.com/NHfc3Wd.png"
        NEUTRAL: str = "https://i.imgur.com/fcKmaLr.png"
        LOVE: str = "https://i.imgur.com/lH71Gmf.png"
        POO: str = "https://i.imgur.com/lj6XmQI.png"
        QUESTION: str = "https://i.imgur.com/52zSz3H.png"
        SAD: str = "https://i.imgur.com/iOWD0yL.png"
        SHOCKED: str = "https://i.imgur.com/U7rBtRu.png"
        SLEEPY: str = "https://i.imgur.com/6bmFC6l.png"
        SWEAT: str = "https://i.imgur.com/KbWJZkD.png"
        KISS: str = "https://i.imgur.com/vuZeoRO.png"
        SMIRK: str = "https://i.imgur.com/or3cvYB.png"
        XD: str = "https://i.imgur.com/BC0OBa6.png"
        OX: str = "https://i.imgur.com/CiZdJAd.png"
        GRAGAS: str = "https://i.imgur.com/fXf3GnC.png"

        POROGROWINGS: List[str] = [
            "https://i.imgur.com/Eex5g5J.png",
            "https://i.imgur.com/52LLvqI.png",
            "https://i.imgur.com/2vEGssv.png",
            "https://i.imgur.com/PcXqiub.png",
            "https://i.imgur.com/7ohi1cB.png",
            "https://i.imgur.com/VBmrv8w.png",
            "https://i.imgur.com/7bIdncF.png",
            "https://i.imgur.com/gQ79HSq.png",
            "https://i.imgur.com/2gBVwgr.png",
            "https://i.imgur.com/LGM3liY.png",
            "https://i.imgur.com/sGvrPcj.png",
        ]

    class Tournament:
        CLASHBANNER: str = "https://i.imgur.com/GoV9WVk.jpg"
        TROPHY: str = "https://i.imgur.com/GMaULvR.png"

    class Lol:
        @staticmethod
        def profil_icon(id: int):
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{id}.jpeg"

        @staticmethod
        def challenge_icon(id: int, tier: str):
            if tier not in [
                "iron",
                "bronze",
                "silver",
                "gold",
                "platinum",
                "diamond",
                "master",
                "grandmaster",
                "challenger",
            ]:
                raise KeyError(f"tier {tier} is invalide")
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/challenges/config/{id}/tokens/{tier}.png"

        @staticmethod
        def champion_icon(id: int) -> str:
            return f"https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/v1/champion-icons/{id}.png"

        LOGO: str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/splashscreens/lol_icon.png"

        ARAM: str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/aram/img/icon-victory.png"
        RIFT: str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/classic_sru/img/icon-victory.png"

    SABLIER: str = "https://i.imgur.com/2V0xDMW.png"
    PLACEHOLDER: str = "https://i.imgur.com/n8NfUD3.png"
    BANG: str = "https://i.imgur.com/aMhejbX.png"
