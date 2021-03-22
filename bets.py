from time import time
from printutils import apply_indent

class Bet(object):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        self.__bettor_id = bettor_id
        self.__event_id = event_id
        self.__odds = odds
        self.__stake = stake
        self.__matched = 0
        self.__time = time() # TODO

    def match(self, quantity: int) -> int:
        '''
        Matches this bet by the amount defined in 'quantity'.
        Returns how much of the quantity could be matched to this bet.
        '''

        unmatched = self.stake - self.__matched # Calculate how much money is left to be matched
        qty_matched = quantity if quantity < unmatched else unmatched # Calculate how much of this quantity can be matched to this bet
        self.__matched += qty_matched # Update this bet's matched stake

        return qty_matched

    def get_bettor_id(self) -> int:
        '''Returns the id of the agent who placed this bet.'''
        return self.__bettor_id

    def get_event_id(self) -> int:
        '''Returns the id of the event for which this bet was placed.'''
        return self.__event_id

    def get_odds(self) -> int:
        '''Returns the odds of this bet.'''
        return self.__odds

    def get_stake(self) -> int:
        '''Returns the stake of this bet.'''
        return self.__stake

    def get_matched(self) -> int:
        '''Returns how much of this bet has been matched.'''
        return self.__matched

    def get_unmatched(self) -> int:
        return self.__stake - self.__matched

    def get_time(self) -> float:
        '''Returns the time this bet was placed.'''
        return self.__time
    
    def __str__(self) -> str:
        return '{bet_type=%s, bettor_id=%d, event_id=%d, odds=%5.f, stake=%d, time=%f}' % \
               (self._bet_type, self.__bettor_id, self.__event_id, self.__odds, self.__stake, self.__time)

class Back(Bet):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        super().__init__(bettor_id, event_id, odds, stake)
        self._bet_type = "Back"

class Lay(Bet):
    def __init__(self, bettor_id: int, event_id: int, odds: int, stake: int):
        super().__init__(bettor_id, event_id, odds, stake)
        self._bet_type = "Lay"

