from .bettors import *

class SheepBettor(Bettor):
    '''
    A bettor who uses only the market
    '''

    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("PWB", id, balance, 0)

    def on_opinion_update(self, lob_view: dict, percent_complete: float, decimal_odds: np.float32) -> None:
        '''Not implemented since we only use market to form opinion'''
        pass

    def get_best_competetor(self, lob_view: dict) -> None:
        best_odds: int = 100000000
        best_event_id: int = None
        for event_id in lob_view:
            odds = lob_view[event_id]["backs"]["odds"][0]
            

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self._previous_odds is not None and self.get_balance() > 200:
            max_stake = self._get_max_back_stake()
            stake = max_stake if max_stake < 400 else max_stake // 2
            best_competetor_id = np.argmin(self._previous_odds) + 1
            my_odds = self._previous_odds[best_competetor_id - 1]
            new_bet = self._new_back(best_competetor_id, my_odds, stake, time)

        return new_bet
