from bets import *
from bettors.bettors import *
from bettors.naive_bettor import *
from bettors.back_to_lay_bettor import *

from exchange import BettingExchange
from output_odds import plot_odds, plot_positions

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

def get_next_bet(bettor_list: list, lob_view: dict, percent_complete: float, t: int) -> Bet:
    n_bettors = len(bettor_list)
    i: int = 0
    new_bet = None
    bettor: Bettor = None
    while i < n_bettors and new_bet is None:
        '''Select a random bettor'''
        bettor = pick_random_bettor(bettor_list)

        '''Get their bet'''
        new_bet: Bet = bettor.get_bet(lob_view, percent_complete, t)
        i+= 1

    return bettor, new_bet

if __name__ == "__main__":
    '''Load racesim config'''
    track_params, competetor_params = load_racesim_params()
    n_competetors: int = competetor_params.n_competetors

    '''Create Exchange'''
    exchange: BettingExchange = BettingExchange(n_competetors)

    '''Add Bettors'''
    bettors = {}
    for i in range(20):
        n_sims = 2 ** np.random.randint(1, 5)
        bettors[i] = NaiveBettor(id=i, balance=10000, num_simulations=n_sims)

    for i in range(20, 30):
        n_sims = 2 ** np.random.randint(1, 5)
        bettors[i] = BackToLayBettor(id=i, balance=10000, num_simulations=n_sims)

    bettor_list = list(bettors.values())
    n_bettors = len(bettor_list)

    '''Calculate total number of race simulations needed'''
    n_simulations: int = get_num_simulations(bettor_list)
    n_simulations = shift_bit_length(n_simulations)
    print("num simulations: %d" % n_simulations)

    '''Create race simulation instances'''
    race: RaceSimSerial = RaceSimSerial(track_params, competetor_params)
    race_simulations: RaceSimParallel = RaceSimParallel(n_simulations, track_params, competetor_params)

    all_positions = []
    all_odds = []
   
    opinion_update_period: int = 10
    actions_per_period: int = 10
    
    lob_view = exchange.get_lob_view()
    matched_bets = []

    t: int = 0
    bet_expire_time: int = 20
    percent_complete: float = 0.0

    while not race.is_finished():
        '''Get the current competetor positions'''
        competetor_positions = race.get_competetor_positions()
        all_positions.append(competetor_positions)
        print("Running simulations...")

        '''Run all the simulations from these positions'''
        predicted_winners = race_simulations.simulate_races(competetor_positions)
        print("Simulations complete!")

        odds = calculate_decimal_odds(n_competetors, predicted_winners)
        all_odds.append(odds)

        '''Give each bettor their alocated number of simulation results'''
        update_bettor_opinions(lob_view, bettor_list, percent_complete, predicted_winners)

        '''Allow 1 timestep to pass in the 'ground truth' race'''
        race.step(opinion_update_period)
        percent_complete = race.get_percent_complete()

        for i in range(actions_per_period):
            '''Get a bet from a random bettor'''
            rdm_bettor, new_bet = get_next_bet(bettor_list, lob_view, percent_complete, t)

            '''If they want to post a new bet then...'''
            if new_bet is not None:
                matched_this_bet = []

                '''
                Add it to the exchange, and retrieve the bets it was
                matched with (if any) and the cost of placing the bet
                '''
                bet_cost = exchange.add_bet(new_bet, matched_this_bet)

                '''Update the imutable view of the current state of the LOB'''
                lob_view = exchange.get_lob_view()

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
                matched_bet: MatchedBet
                for matched_bet in matched_this_bet:
                    b1Id: int = matched_bet.get_backer_id()
                    b2Id: int = matched_bet.get_layer_id()
                    b1: Bettor = bettors[b1Id]
                    b2: Bettor = bettors[b2Id]
                    b1.bookkeep(matched_bet)
                    b2.bookkeep(matched_bet)

            '''Increment time'''
            t += 1

            for bettor in bettor_list:
                current_bets = bettor.get_active_bets()
                current_bet: Bet
                for current_bet in current_bets:
                    if ((t - current_bet.get_time()) > bet_expire_time and
                        current_bet.get_unmatched() > 0 and
                        not current_bet.is_cancelled()
                    ):
                        exchange.cancel_bet(current_bet)
                        current_bet.cancel()
                        print(current_bet)
                        bettor.cancel_bet(current_bet)

    '''Refund money to bettors from all of their unmatched bets'''
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

    # for b in bettor_list:
    #     print("")
    #     print(b)
    #     for mb in b.get_matched_bets():
    #         print(mb)   

    print(sum_bal)
    print(race.get_winner())

all_positions = np.array(all_positions)
all_odds = np.array(all_odds)

plot_odds(n_competetors, all_odds, "output/odds")
plot_positions(n_competetors, all_positions, "output/positions-odds")