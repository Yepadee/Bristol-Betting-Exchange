from lob import OrderBook
from bets import *
from bettors import *

class BettingExchange(BettingExchangeView):
    def __init__(self, event_ids: list):
        # Construct empy LOB
        self.__lob = {
            event_id : OrderBook(event_id) for event_id in event_ids
        }

        self.__bettors = []

    def __notify_bettors(self) -> None:
        '''
        Notify all bettors that a new bet has taken place
        and give them the opportunity to respond.
        '''
        map(lambda bettor: bettor.respond(self), self.__bettors) # Notify each observer

    def add_bettor(self, bettor: Bettor) -> None:
        '''Register a bettor to recieve updates from the exchange'''
        self.__bettors.append(bettor)

    def add_bet(self, bet: Bet) -> None:
        '''Add a new bet to the exchange'''
        event_id = bet.get_event_id()
        if event_id not in self.__lob:
            raise Exception("Event with id %d does not exist on the exchange!" % event_id)
        self.__lob[event_id].add_bet(bet)
        self.__notify_bettors() # Notify bettors to respond to new bet

    def get_lob_view(self) -> dict:
        return {
            event_id : self.__lob[event_id].get_view() for event_id in self.__lob.keys()
        }

    def distribute_winnings(self, successful_event_id: int) -> None:
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


if __name__ == "__main__":
    exchange = BettingExchange([i+1 for i in range(1)])
    bettor1 = NaiveBettor(id=1, balance=500)
    exchange.add_bettor(bettor1)

    bet1 = Back(bettor_id=12, event_id=1, odds=122, stake=1000)
    bet2 = Back(bettor_id=12, event_id=1, odds=120, stake=1000)
    bet3 = Lay(bettor_id=12, event_id=1, odds=120, stake=1300)
    
    
    print(bettor1)

    exchange.add_bet(bet1)
    exchange.add_bet(bet2)
    print(exchange)

    print(bet1)
    print(bet2)
    print(bet3)

    exchange.add_bet(bet3)
    
    print(exchange)

    print(bet1)
    print(bet2)
    print(bet3)

    exchange.distribute_winnings(1)
    print(exchange.get_lob_view())
