from .bettors import *

class NaiveBettor(Bettor):
    '''A bettor who simply bets on who he thinks will win at the start'''

    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("NAIVE", id, balance, num_simulations)

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        if self._previous_odds is not None and self.get_balance() > 0:
            rdm = np.random.randint(0, 2)

            if rdm == 0:
                if self.get_balance() > 200:
                    max_stake = self._get_max_back_stake()
                    stake = np.random.randint(200, max_stake)
                    best_competetor = np.argmin(self._previous_odds)
                    odds = self._previous_odds[best_competetor]

                    if odds <= 100:
                        odds += 1

                    return self._new_back(best_competetor + 1, odds, stake, time)
            else:
                worst_competetor = np.random.randint(0, self._previous_odds.size)
                odds = self._previous_odds[worst_competetor]

                if odds <= 100:
                    odds += 1

                max_stake = self._get_max_lay_stake(odds)
                if max_stake > 200:
                    stake = np.random.randint(200, max_stake)
                    return self._new_lay(worst_competetor + 1, odds, stake, time)
        
        return None
