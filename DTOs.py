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

class OddsOverview(object):
    def __init__(self, odds: int):
        self.odds = odds
        self.bets = []

    def add_bet(self, bet: Bet):
        self.bets.append(bet)

class OrderBookHalf(object):
    def __init__(self):
        self.total_stakes = {}
        self.bets = {}

    def add_bet(self, bet: Bet):
        if bet.odds in self.total_stakes:
            self.total_stakes[bet.odds] += bet.stake
            self.bets[bet.odds].append(bet)
        else:
            self.total_stakes[bet.odds] = bet.stake
            self.bets[bet.odds] = [bet]
        

class OrderBook(object):
    def __init__(self, event_id: int):
        self.event_id = event_id
        self.backs = OrderBookHalf()
        self.lays = OrderBookHalf()

    def __str__(self):
        return '{event_id=%d, backs=%s, lays=%s}' % \
               (self.event_id, self.best_back, self.best_lay, self.backs, self.lays)

    def add_bet(self, bet: Back) -> None:
        print("Added Back")
        self.backs.add_bet(bet)

    def add_bet(self, bet: Lay) -> None:
        print("Added Lay")
        self.lays.add_bet(bet)