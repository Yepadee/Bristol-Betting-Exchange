from .bettors import *

class SheepBettor(Bettor):
    '''
    A bettor who uses only the market to inform how they should bet.
    '''

    def __init__(self, id: int, balance: int, num_simulations: int, n_events: int, role: str):
        super().__init__("SHP", id, balance, 0, n_events, role)

    def get_best_competitor(self, lob_view: dict) -> int:
        best_odds: int = 100000000
        best_event_id: int = None
        for event_id in lob_view:
            odds = lob_view[event_id]["backs"]["odds"][0]
            if odds < best_odds:
                best_odds = odds
                best_event_id = event_id
        return best_event_id

    def get_worst_competitor(self, lob_view: dict) -> int:
        worst_odds: int = 0
        worst_event_id: int = None
        for event_id in lob_view:
            odds = lob_view[event_id]["lays"]["odds"][0]
            if odds > worst_odds:
                worst_odds = odds
                worst_event_id = event_id
        return worst_event_id
                

    def get_back_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self.get_balance() > 200:
            max_stake = self._get_max_back_stake()
            stake = max_stake if max_stake < 400 else max_stake // 2
            best_competetor_id = self.get_best_competitor(lob_view)
            my_odds = lob_view[best_competetor_id]["backs"]["odds"][0] - 1
            new_bet = self._new_back(best_competetor_id, my_odds, stake, time)
        return new_bet

    def get_lay_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self.get_balance() > 200:
            max_stake = self._get_max_lay_stake()
            stake = max_stake if max_stake < 400 else max_stake // 2
            best_competetor_id = self.get_worst_competitor(lob_view)
            my_odds = lob_view[best_competetor_id]["lays"]["odds"][0] + 1
            new_bet = self._new_lay(best_competetor_id, my_odds, stake, time)
        return new_bet
