from bets import *
from bettors.bettors import *
from bettors.back_to_lay_bettor import *
from bettors.lay_to_back_bettor import *
from bettors.predicted_win_bettor import *
from bettors.noise_bettor import *
from bettors.sheep_bettor import *
from bettors.risk_taker_bettor import *

from exchange import BettingExchange
from plot_bets import plot_bets

import random
import json
import sys
from functools import reduce
from time import time

sys.path.append('../BBE-Racing-Sim/')
from racesim import *
from sim_output import plot_winners
from plot import plot_odds, plot_positions

current_id: int = 0

def load_bettor(bettor_type: str, role: str, balance: int, rng1: int, rng2: int, n_events: int, all_bettors: dict) -> None:
    global current_id

    n_sims: int = np.random.randint(rng1, rng2 + 1)
    bettor: Bettor = None

    if bettor_type == "BTL":
        bettor = BackToLayBettor(current_id, balance, n_sims, n_events)
    elif bettor_type == "LTB":
        bettor = LayToBackBettor(current_id, balance, n_sims, n_events)
    elif bettor_type == "PWB":
        bettor = PredictedWinBettor(current_id, balance, n_sims, n_events, role)
    elif bettor_type == "NSE":
        bettor = NoiseBettor(current_id, balance, n_sims, n_events, role)
    elif bettor_type == "SHP":
        bettor = SheepBettor(current_id, balance, n_sims, n_events, role)
    elif bettor_type == "RTB":
        bettor = RiskTakerBettor(current_id, balance, n_sims, n_events, role)
    else:
        raise Exception("ERROR: '%s' is an invalid bettor type!" % bettor_type)

    all_bettors[current_id] = bettor
    current_id += 1

def load_bettors(all_bettors: dict, bettor_info: dict, n_events: int) -> None:
    bettor_type: str = bettor_info["type"]
    role: str = bettor_info["role"]
    quantity: int = bettor_info["quantity"]
    balance: int = bettor_info["balance"]
    rng1 = bettor_info["n_sims"][0]
    rng2 = bettor_info["n_sims"][1]
    
    for i in range(quantity):
        load_bettor(bettor_type, role, balance, rng1, rng2, n_events, all_bettors)

def parse_config(n_events: int):
    '''
    Parse BBE config.
    Returns parsed objects.
    '''

    f = open('resources/config.json', 'r', encoding='utf-8')
    config = json.load(f)
    f.close()

    pre_market_time = config["pre_market_time"]
    opinion_update_period = config["opinion_update_period"]
    actions_per_period = config["actions_per_period"]
    bettors = config["bettors"]

    all_bettors = {}
    for bettor_info in bettors:
        load_bettors(all_bettors, bettor_info, n_events)

    return pre_market_time, opinion_update_period, actions_per_period, all_bettors

def get_num_simulations(bettors: list) -> int:
    return reduce((lambda acc, b: acc + b.get_num_simulations()), bettors, 0)

def update_bettor_opinions(n_events: int, all_bettors: list, predicted_winners: np.int8) -> None:
    last_index = 0
    bettor: Bettor
    for bettor in all_bettors:
        num_sims = bettor.get_num_simulations()
        result_slice = predicted_winners[last_index : last_index + num_sims]
        decimal_odds = calculate_decimal_odds(n_events, result_slice)
        bettor.on_opinion_update(decimal_odds)
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

def pick_random_bettor(bettors: list) -> Bettor:
    return bettors[random.randint(0, len(bettors) - 1)]

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

def timestep_market(bettors: dict, bettor_list:list, exchange: BettingExchange, percent_complete: float, t:int):
    '''Update the imutable view of the current state of the LOB'''
    lob_view = exchange.get_lob_view()
    #print(lob_view)
    '''Get a bet from a random bettor'''
    rdm_bettor: Bettor
    new_bet: Bet
    rdm_bettor, new_bet = get_next_bet(bettor_list, lob_view, percent_complete, t)

    '''If they want to post a new bet then...'''
    if new_bet is not None:
        '''Cancel all currently held bets'''
        active_bets = rdm_bettor.get_active_bets()
        active_bet: Bet
        for active_bet in active_bets:
            exchange.cancel_bet(active_bet) # Remove bet from exchange
            active_bet.cancel() # Update state of bet
            rdm_bettor.cancel_bet(active_bet) # Remove bet from bettor
        
        '''Update bettor's internal record of currently held bets'''
        rdm_bettor.add_bet(new_bet)
        
        '''
        Add the new bet to the exchange, and retrieve the bets it
        was matched with (if any) and the cost of placing the bet
        '''
        matched_this_bet = []
        bet_cost = exchange.add_bet(new_bet, matched_this_bet)

        '''
        Charge the bettor the cost of the bet.
        (May be less then estimated cost if it
        was a lay bet and matched with bets with
        better odds)
        '''
        rdm_bettor.deduct_funds(bet_cost)

        '''Update the record of all matched bets'''
        matched_bets.extend(matched_this_bet)

        '''Notify each bettor of the newly matched bets'''
        matched_bet: MatchedBet
        for matched_bet in matched_this_bet:
            b1Id: int = matched_bet.get_backer_id()
            b2Id: int = matched_bet.get_layer_id()
            b1: Bettor = bettors[b1Id]
            b2: Bettor = bettors[b2Id]
            b1.bookkeep(matched_bet)
            b1.on_bet_matched(matched_bet)
            b2.bookkeep(matched_bet)
            b2.on_bet_matched(matched_bet)

    '''Increment time'''
    t += 1    

if __name__ == "__main__":
    '''Load racesim config'''
    track_params, competetor_params = load_racesim_params()
    n_competetors: int = competetor_params.n_competetors

    '''Create Exchange'''
    exchange: BettingExchange = BettingExchange(n_competetors)
    lob_view: dict = exchange.get_lob_view()

    '''Load config & bettors'''
    pre_market_time, opinion_update_period, actions_per_period, bettors = parse_config(n_competetors)

    bettor_list: list = list(bettors.values())
    n_bettors: int = len(bettor_list)

    '''Calculate total number of race simulations needed'''
    n_simulations: int = get_num_simulations(bettor_list)
    #n_simulations = 1<<(n_simulations-1).bit_length()
    print("num simulations: %d" % n_simulations)

    '''Create race simulation instances'''
    race: RaceSimSerial = RaceSimSerial(track_params, competetor_params)
    race_simulations: RaceSimParallel = RaceSimParallel(n_simulations, track_params, competetor_params)

    '''Variables to record activity in race and market'''
    all_positions = []
    all_odds = []
    matched_bets = []

    '''Variables to track time'''
    t: int = -pre_market_time
    percent_complete: float = 0.0

    '''Pre Market Betting'''
    competetor_positions = race.get_competetor_positions()

    '''Run all the simulations from start positions'''
    #print("Running simulations...")
    predicted_winners = race_simulations.simulate_races(competetor_positions)
    #print("Simulations complete!")


    rtime = time()
    '''Give each bettor their alocated number of simulation results'''
    update_bettor_opinions(n_competetors, bettor_list, predicted_winners)
    while t < 1:
        timestep_market(bettors, bettor_list, exchange, percent_complete, t)
        t += 1

    '''In play betting'''
    while not race.is_finished():
        '''Allow 1 timestep to pass in the 'ground truth' race'''
        race.step(opinion_update_period)
        percent_complete = race.get_percent_complete()

        '''Get the current competetor positions'''
        competetor_positions = race.get_competetor_positions()
        all_positions.append(competetor_positions)

        '''Run all the simulations from these positions'''
        #print("Running simulations...")
        predicted_winners = race_simulations.simulate_races(competetor_positions)
        #print("Simulations complete!")

        '''Give each bettor their alocated number of simulation results'''
        update_bettor_opinions(n_competetors, bettor_list, predicted_winners)

        '''Log current overall odds'''
        odds = calculate_decimal_odds(n_competetors, predicted_winners)
        all_odds.append(odds)

        '''Allow time to pass in the market before the next opinion update'''
        for _ in range(actions_per_period):
            timestep_market(bettors, bettor_list, exchange, percent_complete, t)
            t += 1

    '''Refund money to bettors from all of their unmatched bets'''
    bettor: Bettor
    for bettor in bettor_list:
        bettor.cancel_unmatched()

    '''Distribute winnings to all bettors'''
    distribute_winnings(bettors, matched_bets, race.get_winner())

    rtime = time() - rtime
    print("The BBE ran in", rtime, "seconds")

    bettor_list.sort(reverse=True, key=(lambda b: b.get_profit()))
    sum_bal = 0
    b: Bettor
    for b in bettor_list:
        sum_bal += b.get_balance()
        #print(b)

    f = open("output/matched_bets_log.txt", "w", encoding='utf-8')
    for b in bettor_list:
        f.write(str(b))
        for mb in b.get_matched_bets():
            f.write("\n\t" + str(mb))
        f.write("\n")
    f.close()

    # print(lob_view)
    # print(sum_bal)
    print(race.get_winner())

    all_positions = np.array(all_positions)
    all_odds = np.array(all_odds)

    plot_odds(n_competetors, actions_per_period, all_odds, "output/odds")
    plot_positions(n_competetors, actions_per_period, all_positions, "output/positions-odds")
    plot_bets(n_competetors, matched_bets, "output/market-odds")