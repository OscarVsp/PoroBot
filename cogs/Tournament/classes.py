
from faulthandler import disable
import random

import disnake
from utils.data import emotes,color
from utils.FastEmbed import FastEmbed
import json
from datetime import datetime
from typing import List, Union


# Class for the players with attribut name and points
class Player:
    def __init__(self, member : disnake.Member):
        self.member : disnake.Member = member
        self.kills : int = 0
        self.turrets : int = 0
        self.cs : int = 0
    
    @property
    def name(self) -> str:
        return self.member.display_name
    
    @property
    def identity(self) -> str:
        return f"Player {self.name}"
    
    @property
    def id(self) -> int:
        return self.member.id
    
    def __str__(self):
        return f"**{self.name}**"
    
    def addKills(self, kills = 1) -> None:
        self.kills += kills
    
    def addTurrets(self, turrets = 1) -> None:
        self.turrets += turrets
        
    def addCS(self, cs = 1):
        self.cs += cs
        
    def removeKills(self, kills = 1) -> None:
        if self.kills >= kills:
            self.kills -= kills
        else:
            self.kills = 0
        
    def removeTurrets(self, turret = 1) -> None:
        if self.turrets >= turret:
            self.turrets -= turret
        else:  
            self.turrets = 0
        
    def removeCS(self, cs = 1) -> None:
        if self.cs >= cs:
            self.cs -= cs
        else:  
            self.cs = 0
                    
    @property
    def points(self) -> int:
        return self.kills + self.turrets * 0.99 + self.cs * 0.98
    
    async def move_to(self, channel) -> None:
        try:
            await self.member.move_to(channel)
        except:
            pass
        
    def to_dict(self) -> dict:
        return {
            'display_name':self.name,
            'name':self.member.name,
            'id':self.id,
            'points':self.points,
            'kills':self.kills,
            'turrets':self.turrets,
            'cs':self.cs
        }
    

# Class for the teams of two players, with attribut points
class Team:
    
    def __init__(self, players : List[Player], round_n : int, match_n : int, team_n : int):
        self.players : List[Player] = players
        self.round_n : int = round_n
        self.match_n : int = match_n
        self.team_n : int = team_n
        self.kills : int = 0
        self.turrets : int = 0
        self.cs : int = 0
        
    def __str__(self):
        return " & ".join(f"**{p.name}**" for p in self.players)
    
    @property
    def name(self) -> str:
        return " & ".join(p.name for p in self.players)
    
    @property
    def identity(self) -> str:
        return f"Round {self.round_n}, match {self.match_n}, team {self.team_n} : {self.name}"
    
            
    def addKills(self,kills = 1) -> None:
        self.kills += kills
        for player in self.players:
            player.addKills(kills)
    
    def addTurrets(self, turrets = 1) -> None:
        self.turrets += turrets
        for player in self.players:
            player.addTurrets(turrets)
        
    def addCS(self, cs = 1) -> None:
        self.cs += cs
        for player in self.players:
            player.addCS(cs)
        
    def removeKills(self, kills = 1) -> None:
        if self.kills >= kills:
            self.kills -= kills
        else:
            self.kills = 0
        for player in self.players:
            player.removeKills(kills)
        
    def removeTurrets(self, turrets = 1) -> None:
        if self.turrets >= turrets:
            self.turrets -= turrets
        else:
            self.turrets = 0
        for player in self.players:
            player.removeTurrets(turrets)
        
    def removeCS(self, cs = 1) -> None:
        if self.cs >= cs:
            self.cs -= cs
        else:
            self.cs = 0
        for player in self.players:
            player.removeCS(cs)
                
    def reset_score(self) -> None:
        self.removeKills(self.kills)
        self.removeTurrets(self.turrets)
        self.removeCS(self.cs)
        
    @property
    def score(self) -> str:
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
    def points(self) -> int:
        return self.kills + self.turrets * 0.99 + self.cs * 0.98
            
    async def move_to(self, channel):
        for player in self.players:
            await player.move_to(channel)
            
    def to_dict(self) -> dict:
        return {
            'round_id':self.round_n,
            'match_id':self.match_n,
            'team_id':self.team_n,
            'players':self.name,
            'points':self.points,
            'kills':self.kills,
            'turrets':self.turrets,
            'cs':self.cs
        }
    
    
#Class for a match between two teams, with attributs for the teams and the winner, and method to add points to a team
class Match:
    def __init__(self, number : int, entities : Union[List[Player],List[Team]]):
        self.number : int = number
        self.entities : Union[List[Player],List[Team]] = entities
        
    def __str__(self):
        return " vs ".join([f"{entitie}" for entitie in self.entities])

    @property
    def teams(self) -> List[Team]:
        return self.entities
    
    @property
    def player(self) -> List[Player]:
        return self.entities
            
    #property to convert the match to a fields
    @property
    def field(self) -> dict:
        if round(self.entities[0].points) == 2:
            indicators = ['✅','❌']
        elif round(self.entities[1].points) == 2:
            indicators = ['❌','✅']
        else:
            indicators = ['⬛','⬛']
        return f"{indicators[0]}{emotes.num[round(self.entities[0].points)]} {self.entities[0]}\n{indicators[1]}{emotes.num[round(self.entities[1].points)]} {self.entities[1]}"
            
            
    def to_dict(self) -> dict:
        return {
            'number':self.number,
            'entities':[e.to_dict() for e in self.entities],
        }
        
#Class for rounds, with attributs for the matches
class Round:
    def __init__(self, number : int, matches):
        self.number = number
        self.matches = matches
        
        
    def __str__(self):
        return str(self.matches)
   

    
    @property
    def embed(self) -> disnake.Embed:
        if len(self.matches) == 1:
            return FastEmbed(
            title=f"__**ROUND **__{emotes.num[self.number+1]}",
            description= self.matches[0].field,
            color = color.gold
            )
        else:
            return FastEmbed(
            title=f"__**ROUND **__{emotes.num[self.number+1]}",
            color = color.gold,
            fields = [{'name':f"__MATCH __{emotes.alpha[i]}", 'value': match.field,'inline':False} for i, match in enumerate(self.matches)]
            )
            
    def to_dict(self) -> dict:
        return {
            'number':self.number,
            'matches':[m.to_dict() for m in self.matches],
        }
        
    
#Class for the tournament, with attributs for the rounds and the players, and a method to get the players sorted by points 
class Tournament2v2Roll:
    
    seeding_4 : List[List[List[int]]] = [
        [
            [[2, 3],[1, 4]]
        ],[
            [[1, 3],[2, 4]]
        ],[
            [[1, 2],[3, 4]]
        ]
    ]
    
    seeding_5 : List[List[List[int]]] = [
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
    
    seeding_8 : List[List[List[int]]] = [
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
    
    def __init__(self, players : List[Player], name: str, ordered : bool = False):
        self.players : List[Player] = players
        self.name : str = name
        self.ordered : bool = ordered
        self.teams : List[Team] = []
        self.rounds : List[Match] = []
        self.current_round : int = None
        date = datetime.now()
        self.state_file : str = f"cogs/Tournament/{self.name}_state-{date}.json"
        self.logs_file : str = f"cogs/Tournament/{self.name}_logs-{date}.logs"
        
        if len(self.players) == 4:
            self.seeding = Tournament2v2Roll.seeding_4
        elif len(self.players) == 5:
            self.seeding = Tournament2v2Roll.seeding_5
        elif len(self.players) == 8:
            self.seeding = Tournament2v2Roll.seeding_8
            
        self.nb_rounds : int = len(self.seeding)
        self.nb_matchs_per_round : int = len(self.seeding[0])
        
        self.log(f"Initializing tournament {self.name} of {len(self.players)} players.")
        
        
    def __str__(self):
        return str(self.rounds) + " " + str(self.players)



    #method to class to split the players into seven rounds of two match of two teams containing exactly once each player
    def generate(self) -> None:
        if not self.ordered:
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
                                       self.players[self.seeding[i][j][k][1]-1]],
                                       i,j,k))
                matches.append(Match(j,teams))
                self.teams += teams
            self.rounds.append(Round(i, matches))
        self.current_round = self.rounds[0]
        self.log(f"Round generated using the following players order: " + ",".join([str(p.id) for p in self.players]))
        self.save_state()
            
                
            
    #method to get the players sorted by points then by name   
    def getRanking(self) -> List[Player]:
        return sorted(self.players, key=lambda x: (x.points, x.name), reverse=True)
                
    #method to get the next round
    def getNextRound(self) -> Round:
        self.current_round = self.rounds[self.rounds.index(self.current_round) + 1]
        return self.current_round
    
    #method to get the previous round
    def getPreviousRound(self) -> Round:
        self.current_round = self.rounds[self.rounds.index(self.current_round) - 1]
        return self.current_round
    
    def reset_score(self, entity : Union[Player,Team]) -> None:
        entity.reset_score()
        self.save_state()
        self.log(f"Score reset for {entity.identity}")
        
    def addKills(self, entity : Union[Player,Team], kills : int) -> None:
        entity.addKills(kills)
        self.save_state()
        self.log(f"{kills} kills added to {entity.identity}")
        
    def addCS(self, entity : Union[Player,Team], cs : int) -> None:
        entity.addCS(cs)
        self.save_state()
        self.log(f"{cs} cs added to {entity.identity}")
        
    def addKills(self, entity : Union[Player,Team], turret : int) -> None:
        entity.addTurrets(turret)
        self.save_state()
        self.log(f"{turret} turret added to {entity.identity}")
        
        
    def setScore(self, entity : Union[Player,Team], kills : int, turret : int, cs : int) -> None:
        entity.reset_score()
        entity.addKills(kills)
        entity.addTurrets(turret)
        entity.addCS(cs)
        self.save_state()
        self.log(f"Score set for {entity.identity} : kills {kills} | turrets {turret} | cs {cs}.")
        
                
    #property to convert the classement to an embed
    @property
    def classement(self) -> disnake.Embed:
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
            color = color.gold,
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.name}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}**" for p in sorted_player]),'inline':True}
            ]
        )
   
    #property to convert the classement to a embed
    @property
    def detailedClassement(self) -> disnake.Embed:
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
            color = color.gold,
            fields=[
                {'name':"__**Rank**__",'value':"\n".join([f"{ranks[i]}" for i in range(len(sorted_player))]),'inline':True},
                {'name':"__**Players**__",'value':"\n".join([f"**{p.name}**" for p in sorted_player]),'inline':True},
                {'name':"__**Scores**__",'value':"\n".join([f"**{round(p.points)}** *({p.kills}-{p.turrets}-{p.cs})*" for p in sorted_player]),'inline':True}
            ]
        )
        
    #property that return the rules of the tournament as an embed
    @property
    def rules(self) -> disnake.Embed:
        return FastEmbed(
            title = ":scroll: __**RÈGLES**__ :scroll:",
            color = color.gold,
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
                            ❌ __Bans__ : 3 par équipe (à faire via le chat dans le lobby **pré-game**)"""
                },
                {
                    'name':"__**Règles d'un match**__",
                    'value':"""⛔ Interdiction de prendre les healts __extérieurs__ (ceux entre la **T1** et la **T2**).
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
                    *__Exemple :__
                    **Lỳf** est premier avec __14 points__ mais **Gay Prime** est deuxième avec __11 points__\n⏭️ BO5 commençant à **1-0** en faveur de **Lỳf**.*"""
                }
            ]
        )
        
    def to_dict(self) -> dict:
        return {
            'time':str(datetime.now()),
            'name':self.name,
            'nb_players':str(len(self.players)),
            'nb_rounds':str(self.nb_rounds),
            'nb_matches_per_round':str(self.nb_rounds),
            'current_round_index':str(self.rounds.index(self.current_round)),
            'players':[p.to_dict() for p in self.players],
            'teams':[t.to_dict() for t in self.teams],
            'rounds':[r.to_dict() for r in self.rounds]
        }
        
        
    def save_state(self) -> None:
        with open(self.state_file, 'w') as fp:
            json.dump(self.to_dict(), fp, indent=4)
            
    def log(self, txt : str) -> None:
        with open(self.logs_file, 'a') as fp:
            fp.write(f"[{datetime.now()}] " + txt + '\n')
    
        

        
        


    
