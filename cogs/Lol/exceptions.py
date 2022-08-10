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


class MasteriesNotFound(Exception):
    def __init__(self):
        self.message = "Masteries Not Found"
        super().__init__()


class WatcherNotInit(Exception):
    def __init__(self):
        self.message = "Watcher is not initialized"
        super().__init__()
