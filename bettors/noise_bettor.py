from .bettors import *

class NoiseBettor(Bettor):
    '''
    A bettor who picks a random competetor who they think will win.
    '''

    def __init__(self, id: int, balance: int, num_simulations: int, favorite_event_id: int):
        super().__init__("NOISE", id, balance, num_simulations)
        self.__favorite_event_id = favorite_event_id
        self.__has_bet = False

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        if self._previous_odds is not None and self.get_balance() > 0:
            rdm = np.random.randint(0, 2)

            if rdm == 0:
                if self.get_balance() > 200:
                    max_stake = self._get_max_back_stake()
                    stake = np.random.randint(200, max_stake)
                    best_competetor = np.random.randint(0, self._previous_odds.size)
                    odds = self._previous_odds[best_competetor]

                    return self._new_back(best_competetor + 1, odds, stake, time)
            else:
                worst_competetor = np.random.randint(0, self._previous_odds.size)
                odds = self._previous_odds[worst_competetor]

                max_stake = self._get_max_lay_stake(odds)
                if max_stake > 200:
                    stake = np.random.randint(200, max_stake)
                    return self._new_lay(worst_competetor + 1, odds, stake, time)
        
        return None


