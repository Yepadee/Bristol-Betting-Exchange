from bets import Bet

class BettingExchangeView(object):
    def add_bet(self, bet: Bet) -> None:
        pass

class Bettor(object):
    def __init__(self, id: int):
        self.id = id
        self.bets = []

    def respond(exchange: BettingExchangeView):
        '''
        Define the actions the bettor should take in response
        to a new bet being posted to the exchange here.
        '''
        pass

class NaiveBettor(object):
    def respond(exchange: BettingExchangeView):
        pass