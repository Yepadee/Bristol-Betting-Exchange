from bets import *

class OrderBookHalf(object):
    def __init__(self):
        self.__total_stakes = {}
        self.__bets = {}

    def get_total_stakes(self) -> dict:
        return self.__total_stakes

    def add_bet(self, bet: Bet) -> None:
        '''Adds a new bet to the order book'''
        if bet.odds in self.total_stakes:
            self.total_stakes[bet.odds] += bet.stake
            self.__bets[bet.odds].append(bet)
        else:
            self.total_stakes[bet.odds] = bet.stake
            self.__bets[bet.odds] = [bet]

    def has_odds(self, odds: int) -> bool:
        return odds in self.__bets

    def match_bet(self, new_bet: Bet) -> None:
        '''
        Matches a bet from the other side of the lob with the bets currently available at the odds defined in 'new_bet',
        matching the most recent bets first.
        Returns how much of the bet's stake could not be matched
        '''

        if not self.has_odds(new_bet.get_odds()): # If the book does not offer this bet's odds, return the bet's entire stake since none of it could be matched
            return new_bet.get_stake()

        
        bets = self.__bets[new_bet.get_odds()]
        new_bet_stake = new_bet.get_stake()
        qty_to_match = new_bet_stake

        total_matched = 0
        index = 0

        '''
        Match this bet to the bets available at these odds.
        Potentially only one iteration if a single bet exists
        with a stake greater than or equal to the new_bet's stake.
        '''
        while total_matched < new_bet_stake and index < len(bets):
            bet = bets[index] # Retrieve bets in order they were posted
            

            qty_matched = bet.match(qty_to_match) # Match the quantity to this bet and retrieve how much was successfully matched
            qty_to_match -= qty_matched # Update how much quantity is left that we need to match
            total_matched += qty_matched # Update how much we have successfully matched

            if bet.get_stake() == bet.get_matched(): # If all of this bet's stake has been matched, remove it from the lob
                bets.pop(index)

            index += 1

        new_bet.match(total_matched) # Match the original bet with how much we were able to successfully match with bets from the lob
        return new_bet_stake - total_matched


        

class OrderBook(object):
    def __init__(self, event_id: int):
        self.__event_id = event_id
        self.__backs = OrderBookHalf()
        self.__lays = OrderBookHalf()

    def add_bet(self, bet: Back) -> None:
        '''Adds a new back bet to the orderbook'''
        total_unmatched = self.__lays.match_bet(bet) # Attempt to match the bet with bets on the other side of the lob
        if total_unmatched > 0: # If the bet wasnt totally matched, add it to the lob in the hope it can be matched by future bets
            self.__backs.add_bet(bet)

    def add_bet(self, bet: Lay) -> None:
        '''Adds a new lay bet to the orderbook'''
        total_unmatched = self.__backs.match_bet(bet) # Attempt to match the bet with bets on the other side of the lob
        if total_unmatched > 0: # If the bet wasnt totally matched, add it to the lob in the hope it can be matched by future bets
            self.__lays.add_bet(bet)

    def __str__(self) -> str:
        return '{event_id=%d, backs=%s, lays=%s}' % \
               (self.__event_id, self.best_back, self.best_lay, self.__backs, self.__lays)