class NoCurrentTeam(Exception):
    def __init__(self):
        self.message = "Summoner has currently no team."
        super().__init__()

class SummonerNotFound(Exception):
    def __init__(self):
        self.message = "Summoner Datas Not Found"
        super().__init__()
        
class LeagueNotFound(Exception):
    def __init__(self):
        self.message = "League Data Not Found"
        super().__init__()
        
class TeamNotFound(Exception):
    def __init__(self):
        self.message = "Team Not Found"
        super().__init__()