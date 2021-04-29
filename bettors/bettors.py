
from lob import MatchedBet
from bets import Bet
from bets import *
import numpy as np
import sys
sys.path.append('../BBE-Racing-Sim/')
from sim_output import plot_winners_freqs

class Bettor(object):
    def __init__(self, name: str, id: int, balance: int, num_simulations: int):
        self.__name: str = name
        self.__id: int = id
        self.__balance: int = balance
        self.__num_simulations: int = num_simulations
        self.__backs: list = []
        self.__lays: list = []
        self.__active_bets: list = []
        self.__matched_bets: list = []
        self._previous_odds: np.int32 = None
        
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

    def get_active_bets(self) -> list:
        return self.__active_bets

    def get_matched_bets(self) -> list:
        return self.__matched_bets

    def cancel_bet(self, bet: Bet) -> None:
        refund: int = 0
        self.__active_bets.remove(bet)
        
        if type(bet) is Back:
            refund = bet.get_unmatched()
        else:
            refund = bet.get_unmatched_liability()

        self.add_funds(refund)
            
    def _get_max_lay_stake(self, odds) -> int:
        return int(self.get_balance() / (odds / 100.0))

    def _get_max_back_stake(self) -> int:
        return self.get_balance()

    def add_bet(self, bet: Bet):
        '''Add a bet to the bettors record of currently active bets'''
        self.__active_bets.append(bet)

    def _new_back(self, event_id: int, odds: int, stake: int, time: int) -> Back:
        '''Create a new back and add to bettors record of backs'''

        if stake > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % (self.__balance/100.0, stake/100.0))

        if odds <= 100:
            raise Exception("Cannot place a bet with odds %d. Odds must be greater than 1.00!", odds)

        if stake < 200:
            raise Exception("Cannot place a bet with stake %d. Stake must be greater than 200!", stake)

        back = Back(self.__id, event_id, odds, stake, time)
        self.__backs.append(back)
        return back

    def _new_lay(self, event_id: int, odds: int, stake: int, time: int) -> Lay:
        '''Create a new lay and add to bettors record of lays'''
        liability = stake * odds // 100
        if liability > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % (self.__balance/100.0, liability/100.0))
        
        if odds <= 100:
            raise Exception("Cannot place a bet with odds %d. Odds must be greater than 1.00!", odds)

        if stake < 200:
            raise Exception("Cannot place a bet with stake %d. Stake must be greater than 200!", stake)

        lay = Lay(self.__id, event_id, odds, stake, time)
        self.__lays.append(lay)
        return lay

    def add_funds(self, funds: int) -> None:
        self.__balance += funds

    def deduct_funds(self, funds: int) -> None:
        self.__balance -= funds

    def cancel_unmatched(self) -> None:
        '''Cancel all unmatched bets'''
        for bet in self.__active_bets:
            if type(bet) is Back:
                refund = bet.get_unmatched()
            else:
                refund = bet.get_unmatched_liability()
            self.add_funds(refund)
        self.__active_bets = []

    # The following methods should be implemented in a new betting agent:
    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        '''
        Returns either None, a Back or a Lay.
        '''
        pass

    def on_opinion_update(self, lob_view: dict, percent_complete: float, decimal_odds: np.float32) -> None:
        self._previous_odds = decimal_odds
        '''
        Defines the actions the bettor should take in response
        to its opinion of the race outcome being updated.
        '''
        pass

    def bookkeep(self, matched_bet: MatchedBet) -> None:
        '''
        Defines the actions the bettor should take in response
        to new bets being matched.
        '''
        self.__matched_bets.append(matched_bet)

        '''Remove matched bets'''
        self.__active_bets = list(filter(
            (lambda active_bet: active_bet.get_unmatched() > 0),
            self.__active_bets
        ))


    def __str__(self) -> str:
        return '{name=%s, id=%d, balance=£%.2f, n_sims=%d, backs=%d, lays=%d}' % \
               (self.__name, self.__id, self.__balance/100.0, self.__num_simulations, len(self.__backs), len(self.__lays))




