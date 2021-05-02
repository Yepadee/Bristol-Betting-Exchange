from .bettors import *

class NoiseBettor(Bettor):
    '''
    A bettor who picks a bet totally at random.
    '''

    def __init__(self, id: int, balance: int, num_simulations: int, n_events: int):
        super().__init__("NOISE", id, balance, num_simulations)
        self.__favorite_event_id = np.random.randint(1, n_events + 1)

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self._previous_odds is not None and self.get_balance() > 0:
            rdm = np.random.randint(0, 2)

            if rdm == 0:
                if self.get_balance() > 200:
                    max_stake = self._get_max_back_stake()
                    stake = max_stake if max_stake < 400 else max_stake // 2
                    favorite_event_id = self.__favorite_event_id
                    odds = self._previous_odds[favorite_event_id - 1]
                    new_bet = self._new_back(favorite_event_id, odds, stake, time)
            else:
                worst_competetor = np.random.randint(0, self._previous_odds.size)
                odds = self._previous_odds[worst_competetor]

                max_stake = self._get_max_lay_stake(odds)
                if max_stake > 200:
                    stake = np.random.randint(200, max_stake)
                    new_bet = self._new_lay(worst_competetor + 1, odds, stake, time)
        
        return new_bet


