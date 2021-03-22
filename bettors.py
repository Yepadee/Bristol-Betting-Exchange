from bets import Bet
from printutils import Printable

class BettingExchangeView(Printable):
    def add_bet(self, bet: Bet) -> None:
        pass

class Bettor(Printable):
    def __init__(self, id: int):
        self.id = id
        self.bets = []

    def respond(exchange: BettingExchangeView):
        '''
        Define the actions the bettor should take in response
        to a new bet being posted to the exchange here.
        '''
        pass

class NaiveBettor(Printable):
    def respond(exchange: BettingExchangeView):
        pass