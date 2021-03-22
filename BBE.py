from DTOs import *

from bettors import *

class BettingExchangeView(object):
    def add_bet(self, bet: Bet) -> None:
        pass

class BettingExchange(BettingExchangeView):
    def __init__(self, event_ids: list):
        # Construct empy LOB
        self.bets = {}
        self.lob = {
            event_id : OrderBook(event_id) for event_id in event_ids
        }
        self.lob_anon = {
            event_id : OrderBook(event_id) for event_id in event_ids
        }
        self.observers = []

    def add_observer(self, bettor: Bettor) -> None:
        self.observers.append(bettor)

    def __notify_obeservers(self) -> None:
        map(lambda bettor: bettor.respond(self), self.observers) # Notify each observer

    def add_bet(self, bet: Bet) -> None:
        self.lob[bet.event_id].add_bet(bet)
        self.bets[bet.id] = bet
        self.__notify_obeservers() # Notify observers to respond to new bet

    def distribute_winnings(successful_event_id: int) -> None:
        pass





if __name__ == "__main__":
    exchange = BettingExchange([i+1 for i in range(20)])
    bet = Back(12, 102, 12, 12)
    print(bet)
