#import the required modules
import random
from utils.data import emotes
from utils.FastEmbed import FastEmbed


# Class for the players with attribut name and points
class Player:
    def __init__(self, member):
        self.member = member
        self.kills = 0
        self.turrets = 0
        self.cs = 0
    
    @property
    def name(self):
        return self.member.display_name
    
    def __str__(self):
        return f"**{self.name}**"
    
    def addKills(self, kills = 1):
        self.kills += kills
    
    def addTurrets(self, turrets = 1):
        self.turrets += turrets
        
    def addCS(self, cs = 1):
        self.cs += cs
        
    def removeKills(self, kills = 1):
        if self.kills >= kills:
            self.kills -= kills
        else:
            self.kills = 0
        
    def removeTurrets(self, turret = 1):
        if self.turrets >= turret:
            self.turrets -= turret
        else:  
            self.turrets = 0
        
    def removeCS(self, cs = 1):
        if self.cs >= cs:
            self.cs -= cs
        else:  
            self.cs = 0
                    
    @property
    def points(self):
        return self.kills + self.turrets * 0.99 + self.cs * 0.98
    
    async def move_to(self, channel):
        try:
            await self.member.move_to(channel)
        except:
            pass
    

# Class for the teams of two players, with attribut points
class Team:
    def __init__(self, players):
        self.players = players
        self.kills = 0
        self.turrets = 0
        self.cs = 0
        
    def __str__(self):
        return " & ".join(f"**{p.name}**" for p in self.players)
    
    @property
    def name(self):
        return " & ".join(p.name for p in self.players)
    
            
    def addKills(self,kills = 1):
        self.kills += kills
        for player in self.players:
            player.addKills(kills)
    
    def addTurrets(self, turrets = 1):
        self.turrets += turrets
        for player in self.players:
            player.addTurrets(turrets)
        
    def addCS(self, cs = 1):
        self.cs += cs
        for player in self.players:
            player.addCS(cs)
        
    def removeKills(self, kills = 1):
        if self.kills >= kills:
            self.kills -= kills
        else:
            self.kills = 0
        for player in self.players:
            player.removeKills(kills)
        
    def removeTurrets(self, turrets = 1):
        if self.turrets >= turrets:
            self.turrets -= turrets
        else:
            self.turrets = 0
        for player in self.players:
            player.removeTurrets(turrets)
        
    def removeCS(self, cs = 1):
        if self.cs >= cs:
            self.cs -= cs
        else:
            self.cs = 0
        for player in self.players:
            player.removeCS(cs)
                
    def reset_score(self):
        self.removeKills(self.kills)
        self.removeTurrets(self.turrets)
        self.removeCS(self.cs)
        
    @property
    def score(self):
        score = ""
        if self.kills > 0:
            score += f"{self.kills} kills & "
        if self.turrets > 0:
            score += f"{self.turrets} turrets & "
        if self.cs > 0:
            score += f"{self.cs} CS & "
        if score == "":
            score = "Nothing"
        else:
            score = score[:-3]
        return score
        
    @property
    def points(self):
        return self.kills + self.turrets * 0.99 + self.cs * 0.98
            
    async def move_to(self, channel):
        for player in self.players:
            await player.move_to(channel)
    
    
#Class for a match between two teams, with attributs for the teams and the winner, and method to add points to a team
class Match:
    def __init__(self, entities):
        self.entities = entities
        
    def __str__(self):
        return " vs ".join([f"{entitie}" for entitie in self.entities])

    @property
    def teams(self):
        return self.entities
    
    @property
    def player(self):
        return self.entities
            
    #property to convert the match to a fields
    @property
    def field(self):
        if round(self.entities[0].points) == 2:
            indicators = ['✅','❌']
        elif round(self.entities[1].points) == 2:
            indicators = ['❌','✅']
        else:
            indicators = ['⬛','⬛']
        return f"{indicators[0]}{emotes.num[round(self.entities[0].points)]} {self.entities[0]} \n {indicators[1]}{emotes.num[round(self.entities[1].points)]} {self.entities[1]}"
            
            
        
#Class for rounds, with attributs for the matches
class Round:
    def __init__(self, number : int, matches):
        self.number = number
        self.matches = matches
        
        
    def __str__(self):
        return str(self.matches)
   

    
    @property
    def embed(self):
        if len(self.matches) == 1:
            return FastEmbed(
            title=f"__**ROUND **__{emotes.num[self.number+1]}",
            description= self.matches[0].field
            )
        else:
            return FastEmbed(
            title=f"__**ROUND **__{emotes.num[self.number+1]}",
            fields = [{'name':f"__MATCH __{emotes.alpha[i]}", 'value': match.field,'inline':False} for i, match in enumerate(self.matches)]
            )
        
    
#Class for the tournament, with attributs for the rounds and the players, and a method to get the players sorted by points 
class Tournament2v2Roll:
    
    seeding_4 = [
        [
            [[2, 3],[1, 4]]
        ],[
            [[1, 3],[2, 4]]
        ],[
            [[1, 2],[3, 4]]
        ]
    ]
    
    seeding_5 = [
        [
            [[4, 5],[2, 3]]
        ],[
            [[1, 3],[2, 4]]
        ],[
            [[1, 5],[3, 4]]
        ],[
            [[2, 5],[1, 4]]
        ],[
            [[1, 2],[3, 5]]
        ]
    ]
    
    seeding_8 = [
        [
            [[3, 4],[7, 8]],
            [[5, 6],[1, 2]]
        ],[
            [[6, 8],[5, 7]],
            [[1, 3],[2, 4]]
        ],[
            [[1, 4],[5, 8]],
            [[6, 7],[2, 3]]
        ],[
            [[4, 8],[2, 6]],
            [[3, 7],[1, 5]]
        ],[
            [[3, 8],[1, 6]],
            [[2, 5],[4, 7]]
        ],[
            [[2, 8],[3, 5]],
            [[4, 6],[1, 7]]
        ],[
            [[1, 8],[2, 7]],
            [[4, 5],[3, 6]]
        ]
    ]
    
    def __init__(self, players):
        self.players = players
        self.teams = []
        self.rounds = []
        self.current_round = None
        
        if len(self.players) == 4:
            self.seeding = Tournament2v2Roll.seeding_4
        elif len(self.players) == 5:
            self.seeding = Tournament2v2Roll.seeding_5
        elif len(self.players) == 8:
            self.seeding = Tournament2v2Roll.seeding_8
            
        self.nb_rounds = len(self.seeding)
        self.nb_matchs_per_round = len(self.seeding[0])
        
    def __str__(self):
        return str(self.rounds) + " " + str(self.players)


    #method to class to split the players into seven rounds of two match of two teams containing exactly once each player
    def generate(self):
        random.shuffle(self.players)
        #round loop
        for i in range(self.nb_rounds):
            matches = []
            #match loop
            for j in range(self.nb_matchs_per_round):
                teams = []
                #team loop
                for k in range(2):
                    teams.append(Team([self.players[self.seeding[i][j][k][0]-1],
                                      self.players[self.seeding[i][j][k][1]-1]]))
                matches.append(Match(teams))
            self.rounds.append(Round(i, matches))
        self.current_round = self.rounds[0]
                
            
    #method to get the players sorted by points then by name   
    def getRanking(self):
        return sorted(self.players, key=lambda x: (x.points, x.name), reverse=True)
                
    #method to get the next round
    def getNextRound(self):
        self.current_round = self.rounds[self.rounds.index(self.current_round) + 1]
        return self.current_round
    
    #method to get the previous round
    def getPreviousRound(self):
        self.current_round = self.rounds[self.rounds.index(self.current_round) - 1]
        return self.current_round
                
    #property to convert the classement to an embed
    @property
    def classement(self):
        sorted_player = self.getRanking()
        ranks = []
        for i in range(len(sorted_player)):
            if i == 0:
                ranks.append(f"{emotes.rank[i]}")
            elif sorted_player[i].points == sorted_player[i-1].points:
                ranks.append(ranks[-1])
            else:
                ranks.append(f"{emotes.rank[i]}")
        return FastEmbed(
            title = "__**CLASSEMENT**__",
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.name}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}**" for p in sorted_player]),'inline':True}
            ]
        )
   
    #property to convert the classement to a embed
    @property
    def detailedClassement(self):
        sorted_player = self.getRanking()
        ranks = []
        for i in range(len(sorted_player)):
            if i == 0:
                ranks.append(f"{emotes.rank[i]}")
            elif sorted_player[i].points == sorted_player[i-1].points:
                ranks.append(ranks[-1])
            else:
                ranks.append(f"{emotes.rank[i]}")
        return FastEmbed(
            title = "__**CLASSEMENT**__",
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.name}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}** *({p.kills}-{p.turrets}-{p.cs})*" for p in sorted_player]),'inline':True}
            ]
        )
        
    #property that return the rules of the tournament as an embed
    @property
    def rules(self):
        return FastEmbed(
            title = ":scroll: __**RÈGLES**__ :scroll:",
            fields = [
                {
                    'name':"__**Format du tournoi**__",
                    'value':f"""Le tournoi se joue individuellement mais les matchs se font par __équipe de 2__. Ces équipes changent à chaque match. Ceci est fait en s'assurant que chacun joue
                            ✅ __avec__ chaque autres joueurs exactement :one: fois
                            :x: __contre__ chaque autres joueurs exactement :two: fois.
                            Il y aura donc __ {self.nb_rounds} rounds__ avec __{self.nb_matchs_per_round} matchs__ en parallèles."""
                },
                {
                    'name':"__**Format d'un match**__",
                    'value':"""Les matchs sont en __BO1__ se jouant en 2v2 selon le format suivant :
                            🌍 __Map__ : Abime hurlante
                            👓 __Mode__ : Blind
                            ❌ __Bans__ : 3 par équipe (à faire via le chat dans le lobby pré-game)"""
                },
                {
                    'name':"__**Règles d'un match**__",
                    'value':"""⛔ Interdiction de prendre les healts __extérieurs__ (ceux entre la T1 et la T2).
                            ✅ Le suicide est autorisé et ne compte pas comme un kill.
                            ✅ L'achat d'objet lors d'une mort est autorisé."""
                },
                {
                    'name':"__**Score d'un match**__",
                    'value':"""Le match se finit lorsque l'une des deux équipes a __2 points__. Une équipe gagne :one: point pour :
                            ⚔️  __Chaque kills__
                            🧱 __1e tourelle de la game__
                            💰 __1e **joueur** d'une équipe à 100cs__"""
                },
                {
                    'name':"__**Score personnel**__",
                    'value':f"""Les points obtenus en équipe lors d'un match sont ajoutés au score personnel de chaque joueur (indépendamment de qui a marqué le point).
                            À la fin des {self.nb_rounds} rounds, c'est les points personnels qui détermineront le classement."""
                },
                {
                    'name':"__**Égalité**__",
                    'value':f"""En cas d'égalité, on départage avec __kills > Tourelles > 100cs__.
                            En cas d'égalité parfaite pour la première ou deuxième place, un __1v1__ en BO1 est organisé (même règles, mais _1 point__ suffit pour gagner)."""
                },
                {
                    'name':"__**Phase finale**__",
                    'value':f"""À la fin des {self.nb_rounds} rounds, un BO5 en __1v1__ sera joué entre le 1er et le 2ème du classement pour derterminer le grand vainqueur. Pour chaque deux points d'écart, un match d'avance sera accordé au 1er du classement (jusqu'à un maximum de 2 matchs d'avance).
                    __Exemple :__
                    **Lỳf** est premier avec __14 points__ mais **Gay Prime** est deuxième avec __11 points__ ⏭️ BO5 commençant à 1-0 en faveur de **Lỳf**."""
                }
            ]
        )

        
        


    
