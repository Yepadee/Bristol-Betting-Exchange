from lob import OrderBook
from bets import *


class BettingExchange(object):
    def __init__(self, n_events):
        # Construct empy LOB
        self.__lob = {
            event_id : OrderBook(event_id) for event_id in range(1, n_events+1)
        }
        self.__n_events = n_events
        self.__lob_view: dict = {}
        
    def __publish_lob(self) -> None:
        self.__lob_view = {
            event_id : self.__lob[event_id].get_view() for event_id in self.__lob.keys()
        }

    def add_bet(self, bet: Bet, matched_bets: list) -> int:
        '''
        Add a new bet to the exchange.
        Fills 'matched_bets' with the resultant matches from
        adding this bet to the exchange.
        Returns the cost of placing this bet
        '''
        event_id = bet.get_event_id()
        if event_id not in self.__lob:
            raise Exception("Event with id %d does not exist on the exchange!" % event_id)
        
        bet_cost = self.__lob[event_id].add_bet(bet, matched_bets)
        return bet_cost

    def cancel_bet(self, bet: Bet) -> int:
        '''
        Cancel a bet from the exchange.
        '''
        self.__lob[bet.get_event_id()].cancel_bet(bet)

    def get_lob_view(self) -> dict:
        '''Retrieve a view of the exchange's limit order book'''
        self.__publish_lob()
        return self.__lob_view

    def get_n_events(self) -> int:
        '''Returns number of available events to bet on'''
        return self.__n_events

    def __str__(self) -> str:
        return (
            'lobs: {\n%s\n},\n'
        ) % (
            apply_indent(",\n".join(map((lambda x: "{\n%s\n}" % apply_indent(str(x))), self.__lob.values())))
        )

