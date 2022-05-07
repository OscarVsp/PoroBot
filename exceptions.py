from pyot.core.exceptions import PyotException,NotFound,RateLimited,ServerError

class RiotException(Exception):
    pass

class NoCurrentTeam(RiotException):
    def __init__(self):
        self.message = "Summoner has currently no team."
        super().__init__()

class DataNotFound(NotFound):
    def __init__(self):
        self.message = "Data Not Found"
        super().__init__()

class BeingRateLimited(RateLimited):
    def __init__(self):
        self.message = "We are being rate limited"
        super().__init__()

class ServerErrorResponse(ServerError):
    def __init__(self,code):
        self.message = f"Server error, code : {code}"
        super().__init__(code)

class GuildNotFound(Exception):
    def __init__(self,guild_name):
        self.message = 'Guild "'+guild_name+'" was not found.'
        super().__init__(self.message)