from .bettors import *

class NoiseBettor(Bettor):
    def __init__(self, id: int, balance: int, num_simulations: int, favorite_event_id: int):
        super().__init__("NAIVE", id, balance, num_simulations)
        self.__favorite_event_id = favorite_event_id
        self.__has_bet = False

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        if self.get_balance() > 200:
            pass


