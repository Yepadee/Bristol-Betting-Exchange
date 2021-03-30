from lob import OrderBook
from bets import *
from bettors import Bettor, BettingExchangeView
from functools import reduce
import random
import numpy as np


class BettingExchange(BettingExchangeView):
    def __init__(self, n_events):
        # Construct empy LOB
        self.__lob = {
            event_id : OrderBook(event_id) for event_id in range(1, n_events+1)
        }
        self.__n_events = n_events
        self.__bettors: list = []
        self.__lob_view: dict = {}
        self.__has_new_bets = False

    def __notify_bettors_market_change(self) -> None:
        '''
        Notify all bettors that a new bet has taken place
        and give them the opportunity to respond
        '''
        self.__publish_lob()
        indeces = list(range(len(self.__bettors)))
        random.shuffle(indeces)
        map(lambda i: self.__bettors[i].on_market_change(self), indeces) # Notify each observer
        
    def __publish_lob(self) -> None:
        self.__lob_view = {
            event_id : self.__lob[event_id].get_view() for event_id in self.__lob.keys()
        }
    
    def open_market(self) -> None:
        self.__notify_bettors_market_open()

    def add_bettor(self, bettor: Bettor) -> None:
        '''Register a bettor to recieve updates from the exchange'''
        self.__bettors.append(bettor)

    def get_num_simulations(self) -> int:
        return reduce((lambda acc, b: acc + b.get_num_simulations()), self.__bettors, 0)

    def __calculate_winner_probs(self, predicted_winners: np.array(np.int8)):
        winner_freqs = np.zeros(self.__n_events)
        for i in range(self.__n_events):
            event_id = i + 1
            winner_freqs[i] = float(np.count_nonzero(predicted_winners == event_id))

        return winner_freqs / predicted_winners.size

    def update_bettor_opinions(self, percent_complete: float, predicted_winners: np.array(np.int8)) -> None:
        last_index = 0
        bettor: Bettor
        for bettor in self.__bettors:
            num_sims = bettor.get_num_simulations()
            result_slice = predicted_winners[last_index : last_index + num_sims]
            winner_probs = self.__calculate_winner_probs(result_slice)
            bettor.on_opinion_update(self, percent_complete, winner_probs)
            last_index += num_sims

    def add_bet(self, bet: Bet) -> None:
        '''Add a new bet to the exchange'''
        event_id = bet.get_event_id()
        if event_id not in self.__lob:
            raise Exception("Event with id %d does not exist on the exchange!" % event_id)
        self.__lob[event_id].add_bet(bet)
        self.__has_new_bets = True

    def get_bettor_reponses(self) -> None:
        '''Keep asking bettors to repond until no more bets are placed'''
        while self.__has_new_bets:
            self.__has_new_bets = False
            self.__notify_bettors_market_change()

    def get_lob_view(self) -> dict:
        '''Retrieve a view of the exchange's limit order book'''
        return self.__lob_view

    def get_n_events(self) -> int:
        '''Returns number of available events to bet on'''
        return self.__n_events

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

