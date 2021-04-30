from .bettors import *

class PredictedWinnerBettor(Bettor):
    '''
    A bettor who bets on who they believe will win.
    Only places back bets.
    '''

    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("PWB", id, balance, num_simulations)

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self._previous_odds is not None and self.get_balance() > 200:
            max_stake = self._get_max_back_stake()
            stake = max_stake // 2
            best_competetor_id = np.argmin(self._previous_odds) + 1
            my_odds = self._previous_odds[best_competetor_id - 1]
            new_bet = self._new_back(best_competetor_id, my_odds, stake, time)

        return new_bet
