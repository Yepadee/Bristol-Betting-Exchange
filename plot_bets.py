import matplotlib.pyplot as plt
import os
from lob import MatchedBet
from matplotlib.ticker import ScalarFormatter

def shift_bit_length(x):
    return 1<<(x-1).bit_length()

def plot_bets(n_events: int, matched_bets: list, fig_path: str) -> None:
    _, ax = plt.subplots()

    competetor_odds = {}
    competetor_times = {}

    cm = plt.get_cmap('gist_rainbow')
    colours = [cm(1.*i/n_events) for i in range(n_events)]

    for event_id in range(1, n_events + 1):
        matched_bet: MatchedBet
        for matched_bet in matched_bets:
            if matched_bet.get_event_id() == event_id:
                if event_id not in competetor_odds:
                    competetor_odds[event_id] = []
                    competetor_times[event_id] = []

                competetor_odds[event_id].append(matched_bet.get_odds()/100.0)
                competetor_times[event_id].append(matched_bet.get_time())

    for event_id in competetor_odds.keys():
        ax.scatter(competetor_times[event_id], competetor_odds[event_id], color=colours[event_id-1])

    ax.legend(list(competetor_odds.keys()), title='Horse', bbox_to_anchor=(1.00, 1), loc='upper left', fontsize='x-small')
    
    ax.set_ylabel('Decimal Odds')
    ax.set_xlabel('Time/s')

    

    plt.yscale("log", base=2)
    ax.yaxis.set_major_formatter(ScalarFormatter())
    ax.yaxis.set_minor_formatter(ScalarFormatter())
    
    ax.set_yticks([1.0, 2.0, 4.0, 8.0, 16.0, 32.0])

    dir_path = os.path.dirname(fig_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    plt.savefig(fig_path)
    plt.close()