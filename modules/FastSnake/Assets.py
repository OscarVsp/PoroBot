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
    Alpha : List[str] = [
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
        Coeur : str = ":hearts:"
        Pique : str = ":spade:"
        Carreau : str = ":diamonds:"
        Trefle : str = ":clubs:"
   
    PoroSnack : str = '<:porosnack:908477364135161877>'
    BoudhaPog : str = '<:BoudhaPog:854084071055032340>'
    
    bracket : str = "<:bracketicon:1007206320908271726>"
    
    class Lol:
        
        Logo : str = '<:Lol:658237632786071593>'
        OPGG : str = '<:Opgg:948174103557312563>'
        Captain : str = "<:captain:1007206303992643624>"
        Champion : str = "<:champion:1007206305326452806>"
        Chest : str = "<:chest:1007206306693795930>"
        ChestAcquired : str = "<:chestacquired:1007206299664125952>"
        Trophy : str = "<:trophy:1007206322669879326>"
        
        Rift : str = "<:rift:1007278042923671623>"
        Aram : str = "<:aram:1007278045402517604>"
        
        Mastery : List[str] = [
            "<:mastery:1007206302755340318>",
            "<:mastery:1007206302755340318>",
            "<:mastery2:1007216014662049802>",
            "<:mastery3:1007216010635522118>",
            "<:mastery4:1007216016075542548>",
            "<:mastery5:1007216018067828756>",
            "<:mastery6:1007216019942690816>",
            "<:mastery7:1007216021356167189>"
            ]
            
        class Rune:
            Generic : str = "<:rune:1007206351019180042>"
            Domination : str = "<:runedomination:1007206360640925737>"
            Precision : str = "<:runeprecision:1007206358950621225>"
            Resolve : str = "<:runeresolve:1007206352252309614>"
            Sorcery : str = '<:runesorcery:1007206355867811921>'
            Inspiration : str = '<:runewhimsy:1007206353577721886>'
            
        
        class Position:
            UNSELECTED : str = "<:unselected:1007206323693301853>"
            TOP : str = '<:Top:797548227004071956>'
            JUNGLE : str = '<:Jungle:797548226998829078>'
            MIDDLE : str = '<:Mid:797548226944565298>'
            BOTTOM : str = '<:Bot:829047436563054632>'
            UTILITY : str = '<:Support:797548227347480593>'
            FILL : str = "<:Fill:829062843717386261>"
            
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

        class Rank:
            Generic : str = "<:rankedemblem:1007206349509242880>"
            
            UNRANKED : str = "<:Unranked:829242191020032001>"
            IRON : str = "<:Iron:829240724871577600>"
            BRONZE : str = "<:Bronze:829240724754792449>"
            SILVER : str = "<:Silver:829240724867514378>"
            GOLD : str = "<:Gold:829240724842872872>"
            PLATINUM : str = "<:Platinum:829240724797128754>"
            DIAMOND : str = "<:Diamond:829240724830027796>"
            MASTER : str = "<:Master:829240724943405096>"
            GRANDMASTER : str = "<:Grandmaster:829240724767768576>"
            CHALLENGER : str = "<:Challenger:829240724712456193>"
            
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
        
        BlueEssence : str = "<:blueessence:1007206326742564895>"
        Xp : str = "<:boost:1007206301144715284>"
        

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
        Coeur : List[str] = [
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
        Pique : List[str] = [
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
        Carreau : List[str] = [
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
        Trefle : List[str] = [
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
        Back : str = "https://i.imgur.com/xAegVLz.png"
        
        @classmethod
        def get(cls, key : str) -> Optional[Union[List[str],str]]:
            if key == 'coeur':
                return cls.Coeur
            elif key == 'pique':
                return cls.Pique
            elif key == 'carreau':
                return cls.Carreau
            elif key == 'trefle':
                return cls.Trefle
            elif key == 'back':
                return cls.Back
            else:
                return None
                
    class Poros:
        Angry : str = "https://i.imgur.com/bOH0XUl.png"
        Bluch : str = "https://i.imgur.com/vliXsat.png"
        Cool : str = "https://i.imgur.com/wuPk5Fa.png"
        Crying : str = "https://i.imgur.com/apDuJZW.png"
        Tongue_long : str = "https://i.imgur.com/apDuJZW.png"
        Tongue_short : str = "https://i.imgur.com/NHfc3Wd.png"
        Neutral : str = "https://i.imgur.com/fcKmaLr.png"
        Love : str = "https://i.imgur.com/lH71Gmf.png"
        Poo : str = "https://i.imgur.com/lj6XmQI.png"
        Question : str = "https://i.imgur.com/52zSz3H.png"
        Sad : str = "https://i.imgur.com/iOWD0yL.png"
        Shock : str = "https://i.imgur.com/U7rBtRu.png"
        Sleepy : str = "https://i.imgur.com/6bmFC6l.png"
        Sweat : str = "https://i.imgur.com/KbWJZkD.png"
        Kiss : str = "https://i.imgur.com/vuZeoRO.png"
        Smirk : str = "https://i.imgur.com/or3cvYB.png"
        Xd : str = "https://i.imgur.com/BC0OBa6.png"
        Ox : str = "https://i.imgur.com/CiZdJAd.png"
        Gragas : str = "https://i.imgur.com/fXf3GnC.png"

        Growings : List[str] = [
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
        ClashBanner : str = "https://i.imgur.com/GoV9WVk.jpg"
        Trophy : str = "https://i.imgur.com/GMaULvR.png"
        
    class Lol:
        
        @staticmethod
        def profil_icon(id : int):
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/v1/profile-icons/{id}.jpeg"
        
        @staticmethod
        def challenge_icon(id : int, tier : str):
            if tier not in ['iron','bronze','silver','gold','platinum','diamond','master','grandmaster','challenger']:
                raise KeyError(f"tier {tier} is invalide")
            return f"https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/challenges/config/{id}/tokens/{tier}.png"

        Logo : str = "https://raw.communitydragon.org/pbe/plugins/rcp-be-lol-game-data/global/default/assets/splashscreens/lol_icon.png"
        
        Aram : str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/aram/img/icon-victory.png"
        Rift : str = "https://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/default/content/src/leagueclient/gamemodeassets/classic_sru/img/icon-victory.png"
        
        
        
    Sablier : str = "https://i.imgur.com/2V0xDMW.png"
    Placeholder : str = "https://i.imgur.com/n8NfUD3.png"
    Bang_6 : str = "https://i.imgur.com/aMhejbX.png"