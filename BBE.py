from bets import *
from bettors import *
from exchange import BettingExchange

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

def calculate_winner_probs(n_events: int, predicted_winners: np.array(np.int8)) -> np.array(np.float32):
    winner_freqs = np.zeros(n_events)
    for i in range(n_events):
        event_id = i + 1
        winner_freqs[i] = float(np.count_nonzero(predicted_winners == event_id))
    return winner_freqs / predicted_winners.size

def update_bettor_opinions(lob_view: dict, all_bettors: list, percent_complete: float, predicted_winners: np.array(np.int8)) -> None:
    last_index = 0
    bettor: Bettor
    n_events = len(lob_view.keys())
    for bettor in all_bettors:
        num_sims = bettor.get_num_simulations()
        result_slice = predicted_winners[last_index : last_index + num_sims]
        winner_probs = calculate_winner_probs(n_events, result_slice)
        bettor.on_opinion_update(lob_view, percent_complete, winner_probs)
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
    for i in range(100):
        n_sims = 2 ** np.random.randint(2, 9)
        bettors[i] = NaiveBettor(id=i, balance=10000, num_simulations=n_sims)
    # bettors[1] = NaiveBettor(id=1, balance=500, num_simulations=8)
    # bettors[2] = NaiveBettor(id=2, balance=500, num_simulations=16)
    # bettors[3] = NaiveBettor(id=3, balance=500, num_simulations=32)
    # bettors[4] = NaiveBettor(id=4, balance=500, num_simulations=64)
    # bettors[5] = NaiveBettor(id=5, balance=500, num_simulations=128)

    bettor_list = list(bettors.values())

    '''Calculate total number of race simulations needed'''
    n_simulations: int = get_num_simulations(bettor_list)
    n_simulations = shift_bit_length(n_simulations)
    print("num simulations: %d" % n_simulations)

    '''Create race simulation instances'''
    race: RaceSimSerial = RaceSimSerial(track_params, competetor_params)
    race_simulations: RaceSimParallel = RaceSimParallel(n_simulations, track_params, competetor_params)

    t: int = 0
    opinion_update_period: int = 10
    actions_per_period: int = 100
    percent_complete: float = 0.0
    lob_view = exchange.get_lob_view()
    matched_bets = []
    while not race.is_finished():
        competetor_positions = race.get_competetor_positions() # Get the current competetor positions
        print("Running simulations...")
        predicted_winners = race_simulations.simulate_races(competetor_positions) # Run all the simulations from these positions
        
        n_events = exchange.get_n_events()
        plot_winners(n_events, predicted_winners, f'output/{t}.png')
        update_bettor_opinions(lob_view, bettor_list, percent_complete, predicted_winners) # Give each bettor their alocated number of simulation results

        race.step(opinion_update_period) # Allow 1 timestep to pass in the race
        percent_complete = race.get_percent_complete()

        #random.shuffle(bettor_list)
        for i in range(actions_per_period):
            rdm_bettor: Bettor = pick_random_bettor(bettor_list)

            new_bet: Bet = rdm_bettor.get_bet(lob_view, t) # Get their bet
            lob_view = exchange.get_lob_view()

            if new_bet is not None: # If they want to post a new bet
                # print("-----------------------------")
                # print("before: %s" % str(new_bet))
                matched_this_bet = []
                bet_cost = exchange.add_bet(new_bet, matched_this_bet) # Add it to the exchange, and retrieve the bets it was matched with (if any) and the cost of placing the bet.
                # print("after: %s" % str(new_bet))
                # print("cost: %d" % bet_cost)
                # print("matched: ")
                # for mb in matched_this_bet:
                #     print(mb)
                # print("-----------------------------\n")
                rdm_bettor.deduct_funds(bet_cost) # Charge the bettor the cost of the bet. (May be less then estimated cost if it was a lay bet and matched with bets with better odds)
                matched_bets.extend(matched_this_bet)
                bettor: Bettor
                for bettor in bettor_list: # 
                    bettor.on_bets_matched(lob_view, percent_complete, matched_bets)

            t += 1
        print(exchange)

    #print(exchange)
    for bettor in bettor_list:
        bettor.cancel_unmatched()

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
