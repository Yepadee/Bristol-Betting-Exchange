from lob import OrderBook
from bets import *
from bettors import *
from functools import reduce

class BettingExchange(BettingExchangeView):
    def __init__(self, event_ids: list):
        # Construct empy LOB
        self.__lob = {
            event_id : OrderBook(event_id) for event_id in event_ids
        }

        self.__bettors = []

    def __notify_bettors_opinion_update(self) -> None:
        '''Update all bettor's opinions based on the current state of the race'''
        map(lambda bettor: bettor.on_market_open(self), self.__bettors) # Notify each observer

    def __notify_bettors_market_open(self) -> None:
        '''Notify all bettors that the market has opened'''
        map(lambda bettor: bettor.on_market_open(self), self.__bettors) # Notify each observer

    def __notify_bettors_market_change(self) -> None:
        '''
        Notify all bettors that a new bet has taken place
        and give them the opportunity to respond
        '''
        map(lambda bettor: bettor.on_market_change(self), self.__bettors) # Notify each observer

    def add_bettor(self, bettor: Bettor) -> None:
        '''Register a bettor to recieve updates from the exchange'''
        self.__bettors.append(bettor)

    def update_opinions(self, race_state: list) -> None:
        total_sims = reduce((lambda acc, b: acc + b.get_num_simulations()))
        race_results = []

        for bettor in self.__bettors:
            num_sims = bettor.get_num_simulations()

    def add_bet(self, bet: Bet) -> None:
        '''Add a new bet to the exchange'''
        event_id = bet.get_event_id()
        if event_id not in self.__lob:
            raise Exception("Event with id %d does not exist on the exchange!" % event_id)
        self.__lob[event_id].add_bet(bet)
        self.__notify_bettors_market_change() # Notify bettors to respond to new bet

    def get_lob_view(self) -> dict:
        '''Retrieve a view of the exchange's limit order book'''
        return {
            event_id : self.__lob[event_id].get_view() for event_id in self.__lob.keys()
        }

    def distribute_winnings(self, successful_event_id: int) -> None:
        '''Distribute winnings to all bettors based on the outcome of the race'''
        for bettor in self.__bettors:
            bettor.distribute_winnings(successful_event_id)

    def __str__(self) -> str:
        return (
            'lobs: {\n%s\n},\n'
            'bettors: {\n%s\n} '
        ) % (
            apply_indent(",\n".join(map((lambda x: "{\n%s\n}" % apply_indent(str(x))), self.__lob.values()))),
            apply_indent(",\n".join(map((lambda x: "{\n%s\n}" % apply_indent(str(x))), self.__bettors)))
        )

