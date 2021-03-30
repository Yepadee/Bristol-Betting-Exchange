
from bets import Bet
from bets import *
import numpy as np
import sys
sys.path.append('../BBE-Racing-Sim/')
from sim_output import plot_winners_freqs

class BettingExchangeView(object):
    def add_bet(self, bet: Bet) -> None:
        raise Exception("add_bet undefined")

    def cancel_bet(self, bet: Bet) -> None:
        raise Exception("cancel_bet undefined")

    def get_lob_view(self) -> dict:
        raise Exception("get_lob_view undefined")

    def get_n_events(self) -> int:
        raise Exception("get_n_events undefined")

class Bettor(object):
    def __init__(self, name: str, id: int, balance: int, num_simulations: int):
        self.__name: str = name
        self.__id: int = id
        self.__balance: int = balance
        self.__num_simulations: int = num_simulations
        self.__backs: list = []
        self.__lays: list = []
        
    def get_id(self) -> int:
        return self.__id

    def get_balance(self) -> int:
        return self.__balance

    def get_num_simulations(self) -> int:
        return self.__num_simulations

    def get_backs(self) -> list:
        return self.__backs

    def get_lays(self) -> list:
        return self.__lays

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

    def on_opinion_update(self, exchange_view: BettingExchangeView, percent_complete: float, simulation_winner_probs: np.array(np.float32)) -> None:
        '''
        Defines the actions the bettor should take in response
        to its opinion on the race outcome being updated.
        '''
        raise Exception("on_opinion_update undefined")

    def on_market_change(self, exchange_view: BettingExchangeView) -> None:
        '''
        Defines the actions the bettor should take in response
        to a new bet being posted to the exchange here.
        '''
        raise Exception("on_market_change undefined")

    def __str__(self) -> str:
        return '{name=%s, id=%d, balance=£%.2f, backs=%d, lays=%d}' % \
               (self.__name, self.__id, self.__balance/100.0, len(self.__backs), len(self.__lays))

class NaiveBettor(Bettor):
    '''A bettor who simply bets on who he thinks will win at the start'''

    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("NAIVE", id, balance, num_simulations)

    def on_opinion_update(self, exchange_view: BettingExchangeView, percent_complete: float, simulation_winner_probs: np.array(np.float32)) -> None:
        #print(simulation_winner_probs * self.get_num_simulations())
        plot_winners_freqs(exchange_view.get_n_events(), simulation_winner_probs * self.get_num_simulations(), 'output/%d/fig%s.png' % (percent_complete * 100, self.get_id()))

    def on_market_change(exchange_view: BettingExchangeView) -> None:
        lob = exchange_view.get_lob_view()
        print("respond: ")

