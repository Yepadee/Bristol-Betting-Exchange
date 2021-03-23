
from bets import Bet
from bets import *

class BettingExchangeView(object):
    def add_bet(self, bet: Bet) -> None:
        raise Exception("add_bet undefined")

    def get_lob_view(self) -> dict:
        raise Exception("get_lob_view undefined")


class Bettor(object):
    def __init__(self, id: int, balance: int, name: str):
        self.__id = id
        self.__balance = balance
        self.__name = name
        self.__backs = []
        self.__lays = []
        
    def get_id(self) -> int:
        return self.__id

    def get_backs(self) -> list:
        return self.__backs

    def get_lays(self) -> list:
        return self.__lays

    def get_balance(self) -> int:
        return self.__balance

    def _new_back(self, event_id: int, odds: int, stake: int) -> Back:
        '''Create a new back and add to bettors record of backs'''

        if stake > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % self.__balance/100.0, stake/100.0)

        back = Back(self.__id, event_id, odds, stake)
        self.__backs.append(back)
        self.__balance -= stake
        return back

    def _new_lay(self, event_id: int, odds: int, stake: int) -> Lay:
        '''Create a new lay and add to bettors record of lays'''
        liability = stake * odds
        if liability > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % self.__balance/100.0, liability/100.0)
        lay = Lay(self.__id, event_id, odds, stake)
        self.__lays.append(lay)
        self.__balance -= liability
        return lay

    def distribute_winnings(self, successful_event_id: int) -> None:
        for back in self.__backs:
            if back.get_event_id() == successful_event_id:
                self.__balance += back.get_winnings()

        for lay in self.__lays:
            if lay.get_event_id() != successful_event_id:
                self.__balance += lay.get_winnings()
            else:
                self.__balance += lay.get_unmatched_liability() # Return unmatched liability

    def respond(exchange: BettingExchangeView):
        '''
        Define the actions the bettor should take in response
        to a new bet being posted to the exchange here.
        '''
        raise Exception("respond undefined")

    def __str__(self) -> str:
        return '{name=%s, id=%d, balance=£%.2f, backs=%d, lays=%d}' % \
               (self.__name, self.__id, self.__balance/100.0, len(self.__backs), len(self.__lays))

class NaiveBettor(Bettor):
    def __init__(self, id: int, balance: int):
        super().__init__(id, balance, "NAIVE")

    def respond(exchange: BettingExchangeView):
        lob = exchange.get_lob_view()
        print("respond: ", )