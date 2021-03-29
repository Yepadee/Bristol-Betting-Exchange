from lob import OrderBook
from bets import *
from bettors import *
from exchange import BettingExchange

import sys
sys.path.append('../BBE-Racing-Sim/')

from racesim import *



def step(exchange: BettingExchange, race: RaceSimSerial, race_simulations: RaceSimParallel, opinion_update_frequency: int, step_no: int):
    competetor_positions = race.get_competetor_positions()
    predicted_winners = race_simulations.simulate_races(competetor_positions)
    exchange.update_bettor_opinions(step_no, predicted_winners)
    race.step(opinion_update_frequency)
    step_no += opinion_update_frequency

if __name__ == "__main__":
    '''Load racesim config'''
    track_params, competetor_params = load_racesim_params()
    n_competetors: int = competetor_params.n_competetors

    opinion_update_frequency: int = 20
    n_updates = track_params.n_steps // opinion_update_frequency
    print(n_updates)

    '''Create Exchange'''
    exchange: BettingExchange = BettingExchange(n_competetors)

    '''Add Bettors'''
    exchange.add_bettor(NaiveBettor(id=1, balance=500, num_simulations=8))
    exchange.add_bettor(NaiveBettor(id=2, balance=500, num_simulations=16))
    exchange.add_bettor(NaiveBettor(id=3, balance=500, num_simulations=32))
    exchange.add_bettor(NaiveBettor(id=4, balance=500, num_simulations=64))
    exchange.add_bettor(NaiveBettor(id=5, balance=500, num_simulations=128))

    '''Calculate total number of race simulations needed'''
    n_simulations: int = exchange.get_num_simulations()

    '''Create race simulation instances'''
    race: RaceSimSerial = RaceSimSerial(track_params, competetor_params)
    race_simulations: RaceSimParallel = RaceSimParallel(n_simulations, track_params, competetor_params)

    step_no = 0
    while not race.is_finished():
        step(exchange, race, race_simulations, opinion_update_frequency, step_no)
        step_no += opinion_update_frequency
        print(race.is_finished())

    print(race.get_winner())

    #exchange.
    #print(exchange)
    #exchange.distribute_winnings(1)
    #print(exchange.get_lob_view())
