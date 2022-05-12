class NoCurrentTeam(Exception):
    def __init__(self):
        self.message = "Summoner has currently no team."
        super().__init__()

class SumomnerNotFound(Exception):
    def __init__(self):
        self.message = "Data Not Found"
        super().__init__()