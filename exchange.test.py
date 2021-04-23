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

n_competetors: int = 1

'''Create Exchange'''
exchange: BettingExchange = BettingExchange(n_competetors)

back1: Back = Back(1, 1, 120, 300, 1)

matched_bets = []

exchange.add_bet(back1, matched_bets)
print(exchange.get_lob_view())

lay1: Lay = Lay(1, 1, 120, 160, 1)
exchange.add_bet(lay1, matched_bets)
print(exchange.get_lob_view())

s = exchange.cancel_bet(back1)
print(exchange.get_lob_view())

print(back1)
print(lay1)