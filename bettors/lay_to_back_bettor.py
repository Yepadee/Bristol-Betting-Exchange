from .bettors import *

class LayToBackBettor(Bettor):
    '''
    A bettor who attempts the lay to back strategy
    by first placing a lay bet, then placing a back bet at higher odds.
    '''
    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("LTB", id, balance, num_simulations)
        self.__state = 'laying'
        self.__layed_event_id = None
        self.__layed_odds = None
        self.__layed_stake = None

    def __get_overestimated_event(self, lob_view: dict) -> int:
        '''
        Returns the id of the event that is most likely to see
        it's odds increase based on the bettor's opinion
        '''
        biggest_diff = 1 # We want at least some difference (hence why it is not 0)
        best_event = None

        for event_id in lob_view:
            '''Get my predicted odds for this event'''
            predicted_odds = self._previous_odds[event_id-1]
            
            '''Get the best available odds to z for this event from the lob'''
            back_odds = lob_view[event_id]['backs']['odds']
            if len(back_odds) > 0:
                best_back = back_odds[0]
                diff = predicted_odds - best_back
                if diff >= biggest_diff:
                    biggest_diff = diff
                    best_event = event_id

        return best_event

    def __calculate_back_stake(self, back_odds) -> int:
        lay_stake = ((self.__layed_odds // 100) * self.__layed_stake) // (back_odds // 100)
        return lay_stake

    def on_bet_matched(self, matched_bet: MatchedBet) -> None:
        if matched_bet.get_backer_id() == self.get_id():
            '''If our lay bet got matched, update our state'''
            self.__state = 'backing'
        else:
            '''Otherwise, we were the betting party in the bet'''
            self.__state = 'done'

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        if self._previous_odds is not None and self.get_balance() > 0:
            if self.__state == 'laying':
                '''
                Which competetor is likely to see an increase in odds?
                Find a competetor with a back bet available that is lower than our predicted odds.
                '''
                best_event_id = self.__get_overestimated_event(lob_view)

                if best_event_id is not None:
                    available_stake = lob_view[best_event_id]['backs']['stakes'][0]
                    odds = lob_view[best_event_id]['backs']['odds'][0]
                    max_stake = (self._get_max_lay_stake(odds) * 3) // 4
                    bet_stake = available_stake if available_stake < max_stake else max_stake
                    bet_stake = bet_stake if bet_stake > 200 else 200 
                    new_bet = self._new_lay(event_id=best_event_id, odds=odds, stake=bet_stake, time=time)
                    self.__layed_event_id = best_event_id
                    self.__layed_odds = odds
                    self.__layed_stake = bet_stake
                    self.__state = 'backing'

            elif self.__state == 'backing':
                '''
                Place a back bet when the odds available are higher than what we placed a lay bet for.
                '''
                available_backs = lob_view[self.__layed_event_id]['backs']['odds']
                if len(available_backs) > 0:
                    lowest_odds = available_backs[0]
                    if lowest_odds < self.__layed_odds:
                        bet_stake = self.__calculate_back_stake(lowest_odds)
                        max_stake = self._get_max_back_stake()
                        bet_stake = bet_stake if bet_stake < max_stake else max_stake
                        new_bet = self._new_lay(event_id=self.__layed_event_id, odds=lowest_odds, stake=bet_stake, time=time)

        return new_bet




