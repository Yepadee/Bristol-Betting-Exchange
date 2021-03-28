from lob import OrderBook
from bets import *
from bettors import *
from exchange import BettingExchange
import sys
sys.path.append('../BBE-Racing-Sim/')
from racesim import RaceSimSerial, RaceSimParallel, load_racesim



if __name__ == "__main__":
    tp, cp, n = load_racesim()
    print(tp)
    exchange = BettingExchange([i+1 for i in range(1)])
    bettor1 = NaiveBettor(id=1, balance=500, num_simulations=10)
    exchange.add_bettor(bettor1)

    #exchange.
    print(exchange)
    exchange.distribute_winnings(1)
    print(exchange.get_lob_view())
