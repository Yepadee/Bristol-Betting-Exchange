from time import time

class Bet(object):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        self.bettor_id = bettor_id
        self.event_id = event_id
        self.odds = odds
        self.stake = stake
        self.time = time() # TODO
    
    def __str__(self):
        return '{bet_type=%s, bettor_id=%d, event_id=%d, odds=%5.f, stake=%d, time=%f}' % \
               (self._bet_type, self.bettor_id, self.event_id, self.odds, self.stake, self.time)

class Back(Bet):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        super().__init__(bettor_id, event_id, odds, stake)
        self._bet_type = "Back"

class Lay(Bet):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        super().__init__(bettor_id, event_id, odds, stake)
        self._bet_type = "Lay"

