from .bettors import *

class PredictedWinBettor(Bettor):
    '''
    A bettor who places bets that they are most likely to win.
    '''

    def __init__(self, id: int, balance: int, num_simulations: int, n_events: int, role: str):
        super().__init__("PWB", id, balance, num_simulations, n_events, role)

    def get_back_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet: Bet = None
        if self._previous_odds is not None and self.get_balance() > 200:
            max_stake = self._get_max_back_stake()
            stake = max_stake if max_stake < 400 else max_stake // 2
            best_competetor_id = np.argmin(self._previous_odds) + 1
            my_odds = self._previous_odds[best_competetor_id - 1]
            new_bet = self._new_back(best_competetor_id, my_odds, stake, time)
        return new_bet

    def get_lay_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet: Bet = None
        if self._previous_odds is not None and self.get_balance() > 200:
            max_stake = self._get_max_lay_stake()
            stake = max_stake if max_stake < 400 else max_stake // 2
            worst_competetor_id = np.argmax(self._previous_odds) + 1
            my_odds = self._previous_odds[worst_competetor_id - 1]
            new_bet = self._new_back(worst_competetor_id, my_odds, stake, time)
        return new_bet
