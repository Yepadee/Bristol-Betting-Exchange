
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

    def get_bets(self) -> list:
        all_bets = []
        all_bets.extend(self.__backs)
        all_bets.extend(self.__lays)
        return all_bets

    def cancel_bet(self, bet: Bet) -> None:
        refund: int = 0
        bet: Bet
        if type(bet) is Back:
            self.__backs.remove(bet)
            refund = bet.get_unmatched()
        else:
            self.__lays.remove(bet)
            refund = bet.get_unmatched_liability()

        self.add_funds(refund)
            

    def _new_back(self, event_id: int, odds: int, stake: int, time: int) -> Back:
        '''Create a new back and add to bettors record of backs'''

        if stake > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % (self.__balance/100.0, stake/100.0))

        back = Back(self.__id, event_id, odds, stake, time)
        self.__backs.append(back)
        return back

    def _new_lay(self, event_id: int, odds: int, stake: int, time: int) -> Lay:
        '''Create a new lay and add to bettors record of lays'''
        liability = stake * odds // 100
        if liability > self.__balance:
            raise Exception("Bettor has insufficient funds for new back. Has £%.2f, needs £%.2f" % (self.__balance/100.0, liability/100.0))
        lay = Lay(self.__id, event_id, odds, stake, time)
        self.__lays.append(lay)
        return lay

    def add_funds(self, funds: int) -> None:
        self.__balance += funds

    def deduct_funds(self, funds: int) -> None:
        self.__balance -= funds

    def cancel_unmatched(self) -> None:
        back: Back
        sum_refund = 0
        for back in self.__backs:
            self.__balance += back.get_unmatched()
            sum_refund += back.get_unmatched()

        lay: Lay
        for lay in self.__lays:
            self.__balance += lay.get_unmatched_liability()
            sum_refund += lay.get_unmatched_liability()

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

    def on_bets_matched(self, lob_view: dict, percent_complete: float, matched_bets: list) -> None:
        '''
        Defines the actions the bettor should take in response
        to new bets being matched.
        '''
        pass

    def __str__(self) -> str:
        return '{name=%s, id=%d, balance=£%.2f, n_sims=%d, backs=%d, lays=%d}' % \
               (self.__name, self.__id, self.__balance/100.0, self.__num_simulations, len(self.__backs), len(self.__lays))

class NoiseBettor(Bettor):
    def __init__(self, id: int, balance: int, num_simulations: int, favorite_event_id: int):
        super().__init__("NAIVE", id, balance, num_simulations)
        self.__favorite_event_id = favorite_event_id
        self.__has_bet = False

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        if self.get_balance() > 200:
            pass

class NaiveBettor(Bettor):
    '''A bettor who simply bets on who he thinks will win at the start'''

    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("NAIVE", id, balance, num_simulations)

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        if self._previous_odds is not None and self.get_balance() > 0:
            rdm = np.random.randint(0, 2)
            if rdm == 0:
                if self.get_balance() > 200:
                    stake = np.random.randint(200, self.get_balance() + 1)
                    best_competetor = np.argmin(self._previous_odds)
                    odds = self._previous_odds[best_competetor]
                    return self._new_back(best_competetor + 1, odds, stake, time)
            else:
                worst_competetor = np.random.randint(0,self._previous_odds.size)

                odds = self._previous_odds[worst_competetor]
                max_stake = int(self.get_balance() / (odds / 100.0)) #TODO: fix max_stake exceeding balance
                if max_stake > 200:
                    stake = np.random.randint(200, max_stake)
                    return self._new_lay(worst_competetor + 1, odds, stake, time)
        
        return None

    def on_bets_matched(self, lob_view: dict, percent_complete: float, matched_bets: list) -> None:
        #print("respond: %d" % len(matched_bets))
        pass





