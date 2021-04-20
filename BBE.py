from bets import *
from bettors import *
from exchange import BettingExchange
from output_odds import plot_odds

import random

import sys
sys.path.append('../BBE-Racing-Sim/')

from racesim import *
from sim_output import plot_winners

from functools import reduce

def pick_random_bettor(bettors: list) -> Bettor:
    return bettors[random.randint(0, len(bettors) - 1)]

def get_num_simulations(bettors: list) -> int:
    return reduce((lambda acc, b: acc + b.get_num_simulations()), bettors, 0)

def update_bettor_opinions(lob_view: dict, all_bettors: list, percent_complete: float, predicted_winners: np.int8) -> None:
    last_index = 0
    bettor: Bettor
    n_events = len(lob_view.keys())
    for bettor in all_bettors:
        num_sims = bettor.get_num_simulations()
        result_slice = predicted_winners[last_index : last_index + num_sims]
        decimal_odds = calculate_decimal_odds(n_events, result_slice)
        bettor.on_opinion_update(lob_view, percent_complete, decimal_odds)
        last_index += num_sims

def distribute_winnings(bettors: dict, matched_bets: list, successful_event_id: int) -> None:
    '''Distribute winnings to all bettors based on the outcome of the race'''
    matched_bet: MatchedBet
    for matched_bet in matched_bets:
        event_id = matched_bet.get_event_id()
        backer: Bettor = bettors[matched_bet.get_backer_id()]
        layer: Bettor = bettors[matched_bet.get_layer_id()]
        if successful_event_id == event_id:
            backer.add_funds(matched_bet.get_backer_winnings())
        else:
            layer.add_funds(matched_bet.get_layer_winnings())

def shift_bit_length(x):
    return 1<<(x-1).bit_length()

if __name__ == "__main__":
    '''Load racesim config'''
    track_params, competetor_params = load_racesim_params()
    n_competetors: int = competetor_params.n_competetors

    '''Create Exchange'''
    exchange: BettingExchange = BettingExchange(n_competetors)

    '''Add Bettors'''
    bettors = {}
    for i in range(20):
        n_sims = 2 ** np.random.randint(2, 5)
        bettors[i] = NaiveBettor(id=i, balance=10000, num_simulations=n_sims)

    bettor_list = list(bettors.values())

    '''Calculate total number of race simulations needed'''
    n_simulations: int = get_num_simulations(bettor_list)
    n_simulations = shift_bit_length(n_simulations)
    print("num simulations: %d" % n_simulations)

    '''Create race simulation instances'''
    race: RaceSimSerial = RaceSimSerial(track_params, competetor_params)
    race_simulations: RaceSimParallel = RaceSimParallel(n_simulations, track_params, competetor_params)

   
    opinion_update_period: int = 10
    actions_per_period: int = 10
    
    lob_view = exchange.get_lob_view()
    matched_bets = []

    t: int = 0
    percent_complete: float = 0.0

    while not race.is_finished():
        '''Get the current competetor positions'''
        competetor_positions = race.get_competetor_positions()
        print("Running simulations...")
        '''Run all the simulations from these positions'''
        predicted_winners = race_simulations.simulate_races(competetor_positions)
        print("Simulations complete!")

        '''Give each bettor their alocated number of simulation results'''
        update_bettor_opinions(lob_view, bettor_list, percent_complete, predicted_winners)

        '''Allow 1 timestep to pass in the 'ground truth' race'''
        race.step(opinion_update_period)
        percent_complete = race.get_percent_complete()

        for i in range(actions_per_period):
            '''Select a random bettor'''
            rdm_bettor: Bettor = pick_random_bettor(bettor_list)

            '''Get their bet'''
            new_bet: Bet = rdm_bettor.get_bet(lob_view, percent_complete)

            '''Build an imutable view of the current state of the LOB'''
            lob_view = exchange.get_lob_view()

            '''If they want to post a new bet then...'''
            if new_bet is not None:
                matched_this_bet = []

                '''
                Add it to the exchange, and retrieve the bets it was
                matched with (if any) and the cost of placing the bet
                '''
                bet_cost = exchange.add_bet(new_bet, matched_this_bet)

                '''
                Charge the bettor the cost of the bet.
                (May be less then estimated cost if it
                was a lay bet and matched with bets with
                better odds)
                '''
                rdm_bettor.deduct_funds(bet_cost)

                '''Update the record of matched bets'''
                matched_bets.extend(matched_this_bet)

                '''Notify each bettor of the newly matched bets'''
                bettor: Bettor
                for bettor in bettor_list:
                    bettor.on_bets_matched(lob_view, percent_complete, matched_bets)

            '''Increment time'''
            t += 1

    '''Cancel all the bettors unmatched bets'''
    for bettor in bettor_list:
        bettor.cancel_unmatched()

    '''Distribute winnings to all bettors'''
    distribute_winnings(bettors, matched_bets, race.get_winner())

    bettor_list.sort(reverse=True, key=(lambda b: b.get_balance()))
    sum_bal = 0
    b: Bettor
    for b in bettor_list:
        sum_bal += b.get_balance()
        print(b)

    for mb in matched_bets:
        print(mb)   

    print(sum_bal)
    print(race.get_winner())
