import disnake

class emotes:
    rank = ['\U0001f947','\U0001f948','\U0001f949','4\u20e3','5\u20e3','6\u20e3','7\u20e3','8\u20e3','9\u20e3','\U0001f51f','\U0001f1e6','\U0001f1e7','\U0001f1e8','\U0001f1e9','\U0001f1ea']
    num = ['0\u20e3','1\u20e3','2\u20e3','3\u20e3','4\u20e3','5\u20e3','6\u20e3','7\u20e3','8\u20e3','9\u20e3','\U0001f51f','\U0001f1e6','\U0001f1e7','\U0001f1e8','\U0001f1e9','\U0001f1ea']
    alpha = ['\U0001f1e6','\U0001f1e7','\U0001f1e8','\U0001f1e9','\U0001f1ea','\U0001f1eb','\U0001f1ec','\U0001f1ed']
    carte_color = {
        "coeur":":hearts:",
        "pique":":spade:",
        "carreau":":diamonds:",
        "trefle":":clubs:"}
    custom = {
        'wait':"<a:Hourglass:829248200350367754>",
        'yes':'\U00002705',
        'no':'\U0000274c',
        'porosnack':'<:porosnack:908477364135161877>'}
    
    class lol:
        position = {'UNSELECTED':"<:Missing:908411949405069352>",'TOP':'<:Top:797548227004071956>','JUNGLE':'<:Jungle:797548226998829078>','MIDDLE':'<:Mid:797548226944565298>','BOTTOM':'<:Bot:829047436563054632>','UTILITY':'<:Support:797548227347480593>',"FILL":"<:Fill:829062843717386261>"}
        rank = {'UNRANKED':"<:Unranked:829242191020032001>",'IRON':"<:Iron:829240724871577600>",'BRONZE':"<:Bronze:829240724754792449>",'SILVER':"<:Silver:829240724867514378>",'GOLD':"<:Gold:829240724842872872>",'PLATINUM':"<:Platinum:829240724797128754>",'DIAMOND':"<:Diamond:829240724830027796>",'MASTER':"<:Master:829240724943405096>",'GRANDMASTER':"<:Grandmaster:829240724767768576>",'CHALLENGER':"<:Challenger:829240724712456193>"}

    @classmethod
    def number_to_emotes(cls, number : int, size : int = None):
        """
        Take a number and return a list of emotes that correspond to the number
        """
        if size != None:
            number_str = "0"*(size - len(str(number))) + str(number)
        else:
            number_str = str(number)
        return [cls.num[int(chiffre)] for chiffre in number_str]
            

class images:
    cards = {
        "coeur": ["https://i.imgur.com/sSNc54Q.png","https://i.imgur.com/q4M9V3l.png","https://i.imgur.com/OldvcEy.png","https://i.imgur.com/wj1GoO9.png","https://i.imgur.com/0B2Ud1T.png","https://i.imgur.com/eCliqU4.png","https://i.imgur.com/lMbRY2r.png","https://i.imgur.com/cuG1fqu.png","https://i.imgur.com/4NwgCla.png","https://i.imgur.com/2SR4Ial.png"],
        "pique": ["https://i.imgur.com/lrkEiPh.png","https://i.imgur.com/FLWt3us.png","https://i.imgur.com/SlHZ8t4.png","https://i.imgur.com/1mfYaX7.png","https://i.imgur.com/QBHcYfF.png","https://i.imgur.com/q2FfmBf.png","https://i.imgur.com/Hl2Du9R.png","https://i.imgur.com/QDFqD4S.png","https://i.imgur.com/gU5ajry.png","https://i.imgur.com/flk2YDF.png"],
        "carreau": ["https://i.imgur.com/O7cv7tN.png","https://i.imgur.com/kV9fwxW.png","https://i.imgur.com/VLOfZ7b.png","https://i.imgur.com/tVON7pX.png","https://i.imgur.com/gzzilPT.png","https://i.imgur.com/1TdAJDG.png","https://i.imgur.com/tdC9dvu.png","https://i.imgur.com/FilOYsA.png","https://i.imgur.com/pYmcUhJ.png","https://i.imgur.com/hDeAMFI.png"],
        "trefle": ["https://i.imgur.com/QBjfMLu.png","https://i.imgur.com/EF7xnGq.png","https://i.imgur.com/uQ3BIys.png","https://i.imgur.com/z6nYDmr.png","https://i.imgur.com/d3jR6aw.png","https://i.imgur.com/xeNNQKK.png","https://i.imgur.com/HXUu8pk.png","https://i.imgur.com/rHgZm4v.png","https://i.imgur.com/iPpeZmv.png","https://i.imgur.com/idF7THF.png"],
        "back": "https://i.imgur.com/xAegVLz.png"
    }

    class poros:
        angry = "https://i.imgur.com/bOH0XUl.png"
        bluch = "https://i.imgur.com/vliXsat.png"
        cool = "https://i.imgur.com/wuPk5Fa.png"
        crying = "https://i.imgur.com/apDuJZW.png"
        tongue_long = "https://i.imgur.com/apDuJZW.png"
        tongue_short = "https://i.imgur.com/NHfc3Wd.png"
        neutral = "https://i.imgur.com/fcKmaLr.png"
        love = "https://i.imgur.com/lH71Gmf.png"
        poo = "https://i.imgur.com/lj6XmQI.png"
        question = "https://i.imgur.com/52zSz3H.png"
        sad = "https://i.imgur.com/iOWD0yL.png"
        shock = "https://i.imgur.com/U7rBtRu.png"
        sleepy = "https://i.imgur.com/6bmFC6l.png"
        sweat = "https://i.imgur.com/KbWJZkD.png"
        kiss = "https://i.imgur.com/vuZeoRO.png"
        smirk = "https://i.imgur.com/or3cvYB.png"
        xd = "https://i.imgur.com/BC0OBa6.png"
        ox = "https://i.imgur.com/CiZdJAd.png"
        gragas = "https://i.imgur.com/fXf3GnC.png"

        growings = [
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
        
    sablier = "https://i.imgur.com/2V0xDMW.png"
    placeholder = "https://i.imgur.com/n8NfUD3.png"
    
    bang_6 = "https://i.imgur.com/aMhejbX.png"

class color:
    vert = disnake.Color.green()
    bleu = disnake.Color.blue()
    violet = disnake.Color.purple()
    gold = disnake.Color.gold()
    orange = disnake.Color.orange()
    rouge = disnake.Color.red()
    noir = disnake.Color.dark_theme()
    gris = disnake.Color.light_grey()
