from bets import *
from printutils import apply_indent
import numpy as np

class MatchedBet(object):
    def __init__(self, event_id: int, odds: int, stake: int, backer_id: int, layer_id: int):
        self.__event_id = event_id
        self.__odds = odds
        self.__stake = stake
        self.__backer_id = backer_id
        self.__layer_id = layer_id

    def get_event_id(self) -> int:
        return self.__event_id

    def get_odds(self) -> int:
        return self.__odds

    def get_stake(self) -> int:
        return self.__stake

    def get_backer_id(self) -> int:
        return self.__backer_id

    def get_layer_id(self) -> int:
        return self.__layer_id

    def get_layer_winnings(self) -> int:
        return self.get_backer_winnings() # Return layed stake plus liability

    def get_backer_winnings(self) -> int:
        return self.__odds * self.__stake // 100

    def __str__(self) -> str:
        return (
            '{event_id: %d, '
            'odds: %.2f, '
            'stake: £%.2f, '
            'backer_id: %d, '
            'layer_id: %d}'
        ) % (self.__event_id, self.__odds / 100.0, self.__stake / 100.0, self.__backer_id, self.__layer_id)


class OrderBookHalf(object):
    def __init__(self):
        self._total_stakes = {}
        self.__bets = {}

    def add_bet(self, bet: Bet) -> None:
        '''Adds a new bet to the order book'''
        odds = bet.get_odds()
        unmatched = bet.get_unmatched()

        if odds in self.__bets:
            self._total_stakes[odds] += unmatched
            self.__bets[odds].append(bet)
        else:
            self._total_stakes[odds] = unmatched
            self.__bets[odds] = [bet]

    def __match_at_odds(self, bettor_id, odds, stake_to_match, matched_bets) -> int:
        '''
        Match a stake at a specific odds. Returns how much of
        the requested stake could be matched
        '''
        qty_unmatched = stake_to_match
        total_matched = 0
        bets = self.__bets[odds]
        index = 0

        while qty_unmatched > 0 and index < len(bets):
            bet: Bet = bets[index] # Retrieve bets in order of best odds first
            
            qty_matched = bet.match(qty_unmatched) # Match the quantity to this bet and retrieve how much was successfully matched
            matched_bets.append(self._get_matched_bet(bet.get_event_id(), odds, qty_matched, bettor_id, bet.get_bettor_id())) # Add record of how much was matched

            qty_unmatched -= qty_matched # Update how much stake is left that we need to match
            total_matched += qty_matched

            if bet.get_stake() == bet.get_matched(): # If all of this bet's stake has been matched as a result of this match, remove it from the lob
                self.__bets[bet.get_odds()].remove(bet) # TODO: test this acutally works :P

            self._total_stakes[bet.get_odds()] -= qty_matched # Update the total stake at these odds
            if self._total_stakes[bet.get_odds()] == 0:
                self._total_stakes.pop(bet.get_odds())
                self.__bets.pop(bet.get_odds())

            index += 1

        return total_matched

    def match_bet_at_odds(self, new_bet: Bet, matched_bets: list) -> int:
        '''
        Match a bet at the reqeusted odds only.
        Adds any newly matched bets to the provided 'matched_bets' list.
        Returns how much of the stake was not able to be matched
        '''
        if new_bet.get_matched() > 0:
            raise Exception("ERROR: Attempted to match a new bet that has already been matched!")

        bettor_id = new_bet.get_bettor_id()
        odds = new_bet.get_odds()
        new_bet_stake = new_bet.get_stake()
        qty_unmatched = new_bet_stake
        if odds in self.__bets:
            qty_matched = self.__match_at_odds(bettor_id, odds, new_bet_stake, matched_bets)
            qty_unmatched -= qty_matched
            new_bet.match(qty_matched) # Match the original bet with how much we were able to successfully match with bets at the requested odds

        return qty_unmatched

    def match_bet_better_odds(self, new_bet: Bet, matched_bets: list) -> int:
        '''
        Matches a bet only with bets that have odds better than the ones requested.
        Adds any newly matched bets to the provided 'matched_bets' list.
        Mutates the provided 'new_bet' by reducing the stake by how much was matched with bets with better odds
        Returns the resultant cost of the bet. (Could be less for lay bets)
        '''

        if new_bet.get_matched() > 0:
            raise Exception("ERROR: Attempted to match a new bet that has already been matched!")

        bettor_id = new_bet.get_bettor_id()
        odds = new_bet.get_odds()
        new_bet_stake = new_bet.get_stake()
        qty_unmatched = new_bet_stake
        qty_matched = 0

        better_odds: np.int32 = self._get_better_odds(odds)

        '''
        Go through each of the odds that are better than the odds
        provided attepmting to match this bet.
        '''
        index = 0
        bet_cost = 0
        while qty_unmatched > 0 and index < len(better_odds):
            b_odds = better_odds[index]
            matched_at_odds = self.__match_at_odds(bettor_id, b_odds, qty_unmatched, matched_bets)
            qty_unmatched -= matched_at_odds
            bet_cost += self._get_bet_cost(b_odds, matched_at_odds)
            index += 1

        qty_matched = new_bet_stake - qty_unmatched
        new_bet.reduce_stake(qty_matched) # Update stake since some of the stake has now been filled by better odds
        bet_cost += self._get_bet_cost(odds, new_bet.get_unmatched())
        return bet_cost

    def _get_bet_cost(self, odds: int, stake: int) -> int:
        pass

    def _get_ordered_odds(self) -> np.array(np.int32):
        pass

    def _get_better_odds(self, matching_odds: int) -> np.array(np.int32):
        pass

    def _get_matched_bet(self, event_id: int, odds: int, stake: int, new_bettor_id: int, counter_party_id: int) -> MatchedBet:
        pass

    def get_view(self) -> dict:
        '''Returns a copy of the total stakes for each odds'''
        sorted_odds = self._get_ordered_odds()
        return {
            'odds': sorted_odds,
            'stakes': [self._total_stakes[odds] for odds in sorted_odds]
        }
        
    def __str__(self) -> str:
        return apply_indent(" | ".join(map((lambda odds: f'{odds/100.0} : £{self._total_stakes[odds]/100.0}'), self._get_ordered_odds())))

class BackOrderBook(OrderBookHalf):
    def _get_bet_cost(self, odds: int, stake: int) -> int:
        return odds * stake // 100 - stake

    def _get_ordered_odds(self) -> np.array(np.int32): 
        odds = np.array(list(self._total_stakes.keys()))
        odds.sort() # Lowest odds first
        return odds 

    def _get_better_odds(self, matching_odds: int) -> np.array(np.int32):
        ordered_odds = self._get_ordered_odds() 
        return ordered_odds[ordered_odds < matching_odds]

    def _get_matched_bet(self, event_id: int, odds: int, stake: int, new_bettor_id: int, counter_party_id: int) -> MatchedBet:
        return MatchedBet(event_id=event_id, odds=odds, stake=stake, backer_id=counter_party_id, layer_id=new_bettor_id)

class LayOrderBook(OrderBookHalf):
    def _get_bet_cost(self, odds: int, stake: int) -> int:
        return stake

    def _get_ordered_odds(self) -> np.array(np.int32):
        odds = np.array(list(self._total_stakes.keys()))
        odds[::-1].sort() # Highest odds first
        return odds

    def _get_better_odds(self, matching_odds: int):
        ordered_odds = self._get_ordered_odds() 
        return ordered_odds[ordered_odds > matching_odds]

    def _get_matched_bet(self, event_id: int, odds: int, stake: int, new_bettor_id: int, counter_party_id: int) -> MatchedBet:
        return MatchedBet(event_id=event_id, odds=odds, stake=stake, backer_id=new_bettor_id, layer_id=counter_party_id)    


class OrderBook(object):
    def __init__(self, event_id: int):
        self.__event_id = event_id
        self.__backs = BackOrderBook()
        self.__lays = LayOrderBook()
        self.__matched_bets = []

    def add_bet(self, bet: Bet, matched_bets: list) -> int:
        '''
        Adds a new bet to the orderbook.
        Fills the provided list 'matched_bets' with bets that were matched as a 
        result of this new bet.
        Returns the total cost of the bet.
        '''
        order_book: OrderBookHalf = None
        other_book: OrderBookHalf = None
        
        if type(bet) is Back:
            order_book = self.__backs
            other_book = self.__lays
        elif type(bet) is Lay:
            order_book = self.__lays
            other_book = self.__backs
        else:
            raise Exception("Invalid bet type %s!" % str(type(bet)))

        bet_cost = other_book.match_bet_better_odds(bet, matched_bets) # Attempt to match the bet with bets on the other side of the lob with better odds than those requested
        total_unmatched = other_book.match_bet_at_odds(bet, matched_bets)
        if total_unmatched > 0: # If the bet wasnt totally matched, add it to the lob in the hope it can be matched by future bets
            order_book.add_bet(bet)

        return bet_cost

    def get_view(self) -> dict:
        return {
            'backs' : self.__backs.get_view(),
            'lays' : self.__lays.get_view(),
            'matched_bets' : self.__matched_bets
        }

    def __str__(self) -> str:
        indent = 0
        return (
            f'event_id={self.__event_id},\n'
            f'backs={{{str(self.__backs)}}}\n'
            f'lays={{{str(self.__lays)}}}'
        )