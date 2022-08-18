from multiprocessing.sharedctypes import Value
from typing import List, Optional, Union

class Emotes:
    __rank : List[str] = [
        '\U0001f947',
        '\U0001f948',
        '\U0001f949',
        '4\u20e3',
        '5\u20e3',
        '6\u20e3',
        '7\u20e3',
        '8\u20e3',
        '9\u20e3',
        '\U0001f51f',
        '\U0001f1e6',
        '\U0001f1e7',
        '\U0001f1e8',
        '\U0001f1e9',
        '\U0001f1ea'
        ]
    __num : List[str] = [
        '0️⃣',
        '1️⃣',
        '2️⃣',
        '3️⃣',
        '4️⃣',
        '5️⃣',
        '6️⃣',
        '7️⃣',
        '8️⃣',
        '9️⃣'
        ]
    ALPHA : List[str] = [
        '\U0001f1e6',
        '\U0001f1e7',
        '\U0001f1e8',
        '\U0001f1e9',
        '\U0001f1ea',
        '\U0001f1eb',
        '\U0001f1ec',
        '\U0001f1ed'
        ]
    
    class CardColor:
        COEUR : str = ":hearts:"
        PIQUE : str = ":spade:"
        CARREAU : str = ":diamonds:"
        TREFLE : str = ":clubs:"
   
    POROSNACK : str = '<:porosnack:908477364135161877>'
    BOUDHAPOG : str = '<:BoudhaPog:854084071055032340>'
    RESTART : str = '<:restart:1009104340524478534'
    
    BRACKET : str = "<:bracketicon:1007206320908271726>"
    CROSSING_SWORD_BLUE : str = "<:Role_Moderator:1009104341732433930>"
    CROSSING_SWORD_WHITE : str = "<:crossing_sword_gold:1009757236626731018>"
    ROLES : str = "<:roles:1009104343057842398>"
    UTILITY_WHEEL : str = "<:utility:1009104344286761050>"
    GEMME_ANIMED : str = "<a:utility_boosting:1009104346534924309>"
    GEMME : str = "<:utilityboost:1009104353375830088>"
    ARROWS_DOWN : str = "<a:utility_bottompage:1009104348296519690>"
    ARROWS_UP : str = "<a:utility_toppage:1009104349798084759>"
    LOADING : str = "<a:utility6:1009104352239161404>"
    BOOK_PURPLE : str = "<:AcePurpleRoles:1009104397147582515>"
    TWITCH : str = "<:twitch:1009104398091292735>"
    TARGET_BLUE : str = "<:targetblue:1009110751404892211>"
    TARGERT_GOLD : str = "<:target:1009110752721899540>"
    ADD_FRIEND : str = "<:addfriend:1009757240397402133>"
    
    class Lol:
        
        LOGO : str = '<:lol:1007993779984277606>'
        CRIT : str = "<:crit:1009767528395972708>"
        RIOTFIST : str ="<:rp:1009110720559984661>"
        OPGG : str = '<:opgg:1007995866092671006>'
        CHAMPION : str = "<:champion:1007206305326452806>"
        CHEST : str = "<:chest:1007206306693795930>"
        CHESTACQUIRED : str = "<:chestacquired:1007206299664125952>"
        CAPTAIN : str = "<:captain:1007206303992643624>"
        NASHOR : str = "<:nashor:1009110717967904798>"
        HERALD : str = "<:herald:1009110739665043457>"
        TURRET : str = "<:turret:1009760393201201183>"
        GOLD : str = "<:gold:1009759450514587649>"
        CS : str = "<:cs:1009757238254120983>"
        RIFT : str = "<:rift:1007278042923671623>"
        ARAM : str = "<:aram:1007278045402517604>"
        
        TROPHIES : List[str] = [
            "<:trophy:1007206322669879326>",
            "<:trophy4:1009763643312853063>",
            "<:trophy8:1009763639705751643>",
            "<:trophy16:1009763637499531264>"
        ]
        
        class Honor:
            CHILL : str = "<:chill:1009759448367120405>"
            FRIENDLY : str = "<:friendly:1009759446202843186>"
            LEAF : str = "<:honorleaf:1009759443845652530>"
        
        MASTERIES : List[str] = [
            "<:mastery:1007206302755340318>",
            "<:mastery:1007206302755340318>",
            "<:mastery2:1007216014662049802>",
            "<:mastery3:1007216010635522118>",
            "<:mastery4:1007216016075542548>",
            "<:mastery5:1007216018067828756>",
            "<:mastery6:1007216019942690816>",
            "<:mastery7:1007216021356167189>"
            ]
        
        TOKEN : List[str] = [
            "<:tokennone:1009110731142221947>",
            "<:tokeniron:1009110728713707531>",
            "<:tokenbronze:1009110721415622758>",
            "<:tokensilver:1009110734170509422>",
            "<:tokengold:1009110726222286898>",
            "<:tokenplatinum:1009110732887048272>",
            "<:tokendiamond:1009110724313890897>",
            "<:tokenmaster:1009110730345304205>",
            "<:tokengrandmaster:1009110727358939248>",
            "<:tokenchallenger:1009110722657132615>"
        ]
            
            
        class Rune:
            GENERIC : str = "<:rune:1007206351019180042>"
            DOMINATION : str = "<:runedomination:1007206360640925737>"
            PRECISION : str = "<:runeprecision:1007206358950621225>"
            RESOLVE : str = "<:runeresolve:1007206352252309614>"
            SORCERY : str = '<:runesorcery:1007206355867811921>'
            INSPIRATION : str = '<:runewhimsy:1007206353577721886>'
            
        
        class Position:
            UNSELECTED : str = "<:unselected:1007994502318923896>"
            TOP : str = '<:top:1007994503858245672>'
            JUNGLE : str = '<:jungle:1007994500066574407>'
            MIDDLE : str = '<:mid:1007994497810059304>'
            BOTTOM : str = '<:bot:1007994496245579916>'
            UTILITY : str = '<:support:1007994494744002631>'
            FILL : str = "<:fill:1007994493250850897>"
            

            
            @classmethod
            def get(cls, key : str) -> Optional[str]:
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
                
        class Role:
            ADC : str = "<:adc:1009110682639290380>"
            ASSASSIN : str = "<:assassin:1009110684023410698>"
            FIGTHER : str = "<:figher:1009110714327257098>"
            MAGE : str = "<:mage:1009110736691282061>"
            SUPPORT : str = "<:support:1009110748523413556>"
            TANK : str = "<:tank:1009110749727162401>"
            
        class Drake:
            CHEMTECH : str = "<:chemtechdrake:1009110685256515705>"
            CLOUD : str = "<:clouddrake:1009110688876212314>"
            ELDER : str = "<:elderdrake:1009110711957471392>"
            HEXTECH : str = "<:hextechdrake:1009110719196844082>"
            OCEAN : str = "<:oceandrake:1009110741393088604>"
            INFERNAL : str = "<:infernaldrake:1009110735462342656>"
            MOUNTAIN : str = "<:mountainedrake:1009110738335436810>"
            
        class SummonerSpell:
            NONE : str = "<:summonerSpell:1009110747214774402>"
            CLARITY : str = "<:clarity:1009110686573539389>"
            CLEANSE : str = "<:cleanse:1009110687836012704>"
            EXHAUSTE : str = "<:exhaust:1009110713157025832>"
            GHOST : str = "<:ghost:1009110715434545233>"
            HEALT : str = "<:healt:1009110716688633916>"
            SMITE : str = "<:smite:1009110743217618974>"
            SMITE_BLUE : str = "<:smiteblue:1009110744647860394>"
            SMITE_RED : str ="<:smitered:1009110745893576835>"
            TELEPORTATION : str = "<:teleportation:1009110754051493898>"

        class Rank:
            GENERIC : str = "<:rankedemblem:1007206349509242880>"
            
            UNRANKED : str = "<:unranked:1007976696487608431>"
            IRON : str = "<:iron:1007976694646313032>"
            BRONZE : str = "<:bronze:1007976693165727785>"
            SILVER : str = "<:silver:1007992585664614471>"
            GOLD : str = "<:gold:1007976698182111312>"
            PLATINUM : str = "<:platinum:1007976699587207259>"
            DIAMOND : str = "<:diamond:1007976701130715146>"
            MASTER : str = "<:master:1007976691521564692> "
            GRANDMASTER : str = "<:grandmaster:1007976690078732348>"
            CHALLENGER : str = "<:challenger:1007976687948009544>"
            
            
            @classmethod
            def get(cls, key : str) -> Optional[str]:
                if key == "UNRANKED":
                    return cls.UNRANKED
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
        @classmethod
        def get(cls, position : str, rank : str) -> Optional[tuple[str,str]]:
            return (cls.Position.get(position),cls.Rank.get(rank))
        
        BLUEESSENCE : str = "<:blueessence:1007206326742564895>"
        XP : str = "<:boost:1007206301144715284>"
        

    @classmethod
    def Num(cls, number : int, size : int = None) -> str:
        """
        Take a number and return a str of the emotes that correspond to the number.
        """
        if size and size < len(str(number)):
            raise ValueError("Argument size should be greater of equal to the lenght of the number.")
        
        if size != None:
            number_str = "0"*(size - len(str(number))) + str(number)
        else:
            number_str = str(number)
        return "".join([cls.__num[int(chiffre)] for chiffre in number_str])
    
    @classmethod
    def Rank(cls, number : int, size : int = None) -> str:
        """
        Take a number and return a str of the emotes that correspond to the number.
        """
        if size and size < len(str(number+1)):
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
                number_str = str(number+1)
        else :
            number_str = "0"*(size - len(str(number+1))) + str(number+1)
        return "".join([cls.__num[int(chiffre)] for chiffre in number_str])

    
            

class Images:
    
    class Cards:
        COEURS : List[str] = [
            "https://i.imgur.com/sSNc54Q.png",
            "https://i.imgur.com/q4M9V3l.png",
            "https://i.imgur.com/OldvcEy.png",
            "https://i.imgur.com/wj1GoO9.png",
            "https://i.imgur.com/0B2Ud1T.png",
            "https://i.imgur.com/eCliqU4.png",
            "https://i.imgur.com/lMbRY2r.png",
            "https://i.imgur.com/cuG1fqu.png",
            "https://i.imgur.com/4NwgCla.png",
            "https://i.imgur.com/2SR4Ial.png"
            ]
        PIQUES : List[str] = [
            "https://i.imgur.com/lrkEiPh.png",
            "https://i.imgur.com/FLWt3us.png",
            "https://i.imgur.com/SlHZ8t4.png",
            "https://i.imgur.com/1mfYaX7.png",
            "https://i.imgur.com/QBHcYfF.png",
            "https://i.imgur.com/q2FfmBf.png",
            "https://i.imgur.com/Hl2Du9R.png",
            "https://i.imgur.com/QDFqD4S.png",
            "https://i.imgur.com/gU5ajry.png",
            "https://i.imgur.com/flk2YDF.png"
            ]
        CARREAUX : List[str] = [
            "https://i.imgur.com/O7cv7tN.png",
            "https://i.imgur.com/kV9fwxW.png",
            "https://i.imgur.com/VLOfZ7b.png",
            "https://i.imgur.com/tVON7pX.png",
            "https://i.imgur.com/gzzilPT.png",
            "https://i.imgur.com/1TdAJDG.png",
            "https://i.imgur.com/tdC9dvu.png",
            "https://i.imgur.com/FilOYsA.png",
            "https://i.imgur.com/pYmcUhJ.png",
            "https://i.imgur.com/hDeAMFI.png"
            ]
        TREFLES : List[str] = [
            "https://i.imgur.com/QBjfMLu.png",
            "https://i.imgur.com/EF7xnGq.png",
            "https://i.imgur.com/uQ3BIys.png",
            "https://i.imgur.com/z6nYDmr.png",
            "https://i.imgur.com/d3jR6aw.png",
            "https://i.imgur.com/xeNNQKK.png",
            "https://i.imgur.com/HXUu8pk.png",
            "https://i.imgur.com/rHgZm4v.png",
            "https://i.imgur.com/iPpeZmv.png",
            "https://i.imgur.com/idF7THF.png"
            ]
        BACK : str = "https://i.imgur.com/xAegVLz.png"
        
        @classmethod
        def get(cls, key : str) -> Optional[Union[List[str],str]]:
            if key == 'coeur':
                return cls.Coeur
            elif key == 'pique':
                return cls.PIQUES
            elif key == 'carreau':
                return cls.CARREAUX
            elif key == 'trefle':
                return cls.TREFLES
            elif key == 'back':
                return cls.BACK
            else:
                return None
                
    class Poros:
        ANGRY : str = "https://i.imgur.com/bOH0XUl.png"
        BLUCH : str = "https://i.imgur.com/vliXsat.png"
        COOL : str = "https://i.imgur.com/wuPk5Fa.png"
        CRYING : str = "https://i.imgur.com/apDuJZW.png"
        TONGUELONG : str = "https://i.imgur.com/apDuJZW.png"
        TONGUESHORT : str = "https://i.imgur.com/NHfc3Wd.png"
        NEUTRAL : str = "https://i.imgur.com/fcKmaLr.png"
        LOVE : str = "https://i.imgur.com/lH71Gmf.png"
        POO : str = "https://i.imgur.com/lj6XmQI.png"
        QUESTION : str = "https://i.imgur.com/52zSz3H.png"
        SAD : str = "https://i.imgur.com/iOWD0yL.png"
        SHOCKED : str = "https://i.imgur.com/U7rBtRu.png"
        SLEEPY : str = "https://i.imgur.com/6bmFC6l.png"
        SWEAT : str = "https://i.imgur.com/KbWJZkD.png"
        KISS : str = "https://i.imgur.com/vuZeoRO.png"
        SMIRK : str = "https://i.imgur.com/or3cvYB.png"
        XD : str = "https://i.imgur.com/BC0OBa6.png"
        OX : str = "https://i.imgur.com/CiZdJAd.png"
        GRAGAS : str = "https://i.imgur.com/fXf3GnC.png"

        POROGROWINGS : List[str] = [
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
            "https://i.imgur.com/sGvrPcj.png"
            ]

    class Tournament:
        CLASHBANNER : str = "https://i.imgur.com/GoV9WVk.jpg"
        TROPHY : str = "https://i.imgur.com/GMaULvR.png"
        
    class Lol:
        
        @staticmethod
        def profil_icon(id : int):
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{id}.jpeg"
        
        @staticmethod
        def challenge_icon(id : int, tier : str):
            if tier not in ['iron','bronze','silver','gold','platinum','diamond','master','grandmaster','challenger']:
                raise KeyError(f"tier {tier} is invalide")
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/challenges/config/{id}/tokens/{tier}.png"

        LOGO : str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/splashscreens/lol_icon.png"
        
        ARAM : str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/aram/img/icon-victory.png"
        RIFT : str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/classic_sru/img/icon-victory.png"
        
        
        
    SABLIER : str = "https://i.imgur.com/2V0xDMW.png"
    PLACEHOLDER : str = "https://i.imgur.com/n8NfUD3.png"
    BANG : str = "https://i.imgur.com/aMhejbX.png"