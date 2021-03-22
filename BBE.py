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

    def add_bettor(self, bettor: Bettor) -> None:
        '''Register a bettor to recieve updates from the exchange'''
        self.bettors.append(bettor)

    def __notify_bettors(self) -> None:
        '''
        Notify all bettors that a new bet has taken place
        and give them the opportunity to respond.
        '''
        map(lambda bettor: bettor.respond(self), self.__bettors) # Notify each observer

    def add_bet(self, bet: Bet) -> None:
        '''Add a new bet to the exchange'''
        event_id = bet.get_event_id()
        if event_id not in self.__lob:
            raise Exception("Event with id %d does not exist on the exchange!" % event_id)
        self.__lob[event_id].add_bet(bet)
        self.__notify_bettors() # Notify bettors to respond to new bet

    def distribute_winnings(successful_event_id: int) -> None:
        pass

    def __str__(self) -> str:
        return (
            'lobs: {\n%s\n},\n'
            'bettors: {\n%s\n} '
        ) % (
            apply_indent(",\n".join(map((lambda x: "{\n%s\n}" % apply_indent(str(x))), self.__lob.values()))),
            apply_indent(",\n".join(map((lambda x: "{\n%s\n}" % apply_indent(str(x))), self.__bettors)))
        )



if __name__ == "__main__":
    exchange = BettingExchange([i+1 for i in range(3)])
    bet = Back(12, 1, 12, 12)
    print(bet)

    exchange.add_bet(bet)
    print(exchange)
