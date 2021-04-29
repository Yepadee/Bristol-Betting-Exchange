from .bettors import *

class BackToLayBettor(Bettor):
    '''
    A bettor who attempts the back to lay strategy
    by first placing a back bet, then placing a lay bet at lower odds.
    '''
    def __init__(self, id: int, balance: int, num_simulations: int):
        super().__init__("BTL", id, balance, num_simulations)
        self.__state = 'backing'
        self.__backed_event_id = None
        self.__backed_odds = None
        self.__backed_stake = None

    def __get_underestimated_event(self, lob_view: dict) -> int:
        '''
        Returns the id of the event that is most likely to see
        it's odds decrease based on the bettor's opinion
        '''
        biggest_diff = 1 # We want at least some difference (hence why it is not 0)
        best_event = None

        for event_id in lob_view:
            '''Get my predicted odds for this event'''
            predicted_odds = self._previous_odds[event_id-1]
            
            '''Get the best available odds to back for this event from the lob'''
            lay_odds = lob_view[event_id]['lays']['odds']
            if len(lay_odds) > 0:
                best_lay = lay_odds[0]
                diff = best_lay - predicted_odds
                # print("")
                # print(event_id)
                # print(best_lay)
                # print(predicted_odds)
                # print(diff)
                if diff > biggest_diff:
                    biggest_diff = diff
                    best_event = event_id
        # print("best_event: ", best_event)
        # print("")
        return best_event

    def __calculate_lay_stake(self, lay_odds) -> int:
        lay_stake = ((self.__backed_odds // 100) * self.__backed_stake) // (lay_odds // 100)
        return lay_stake

    def get_bet(self, lob_view: dict, percent_complete: float, time: int) -> Bet:
        new_bet = None
        max_stake = self.get_balance() // 4 # Only alocate a quarter of balance for backing 
        if self._previous_odds is not None and self.get_balance() > 0:
            if self.__state == 'backing':
                '''
                Which competetor is likely to see a decrease in odds?
                Find a competetor with a lay bet available that is higher than our predicted odds :)
                '''
                best_event_id = self.__get_underestimated_event(lob_view)

                if best_event_id is not None:
                    available_stake = lob_view[best_event_id]['lays']['stakes'][0]
                    odds = lob_view[best_event_id]['lays']['odds'][0]
                    bet_stake = available_stake if available_stake < max_stake else max_stake
                    bet_stake = bet_stake if bet_stake > 200 else 200 
                    new_bet = self._new_back(event_id=best_event_id, odds=odds, stake=bet_stake, time=time)
                    self.__backed_event_id = best_event_id
                    self.__backed_odds = odds
                    self.__backed_stake = bet_stake
                    self.__state = 'laying'

            elif self.__state == 'laying':
                '''
                Place a lay bet when the odds available are lower than what we placed a back bet for
                '''
                available_backs = lob_view[self.__backed_event_id]['backs']['odds']
                if len(available_backs) > 0:
                    lowest_odds = available_backs[0]
                    if lowest_odds < self.__backed_odds:
                        bet_stake = self.__calculate_lay_stake(lowest_odds)
                        if bet_stake <= self._get_max_lay_stake(lowest_odds):
                            new_bet = self._new_lay(event_id=self.__backed_event_id, odds=lowest_odds, stake=bet_stake, time=time)
                            self.__state = 'done'

        return new_bet




