import numpy as np
import matplotlib.pyplot as plt
import os
from lob import MatchedBet

def plot_bets(n_events: int, matched_bets: list, fig_path: str) -> None:
    _, ax = plt.subplots()

    competetor_odds = {}
    competetor_times = {}

    for event_id in range(1, n_events + 1):
        matched_bet: MatchedBet
        for matched_bet in matched_bets:
            if matched_bet.get_event_id() == event_id:
                if event_id not in competetor_odds:
                    competetor_odds[event_id] = []
                    competetor_times[event_id] = []

                competetor_odds[event_id].append(matched_bet.get_odds())
                competetor_times[event_id].append(matched_bet.get_time())
                
    xs: np.int32 = np.arange(steps)

    cm = plt.get_cmap('gist_rainbow')
    ax.set_prop_cycle(color=[cm(1.*i/n_competetors) for i in range(n_competetors)])
    ax.step(xs, odds/100.0)
    ax.set_ylim([1,20])
    ax.legend(np.arange(1, n_competetors + 1), title='Horse', bbox_to_anchor=(1.00, 1), loc='upper left', fontsize='x-small')
    
    ax.set_ylabel('Decimal Odds')
    ax.set_xlabel('Time/s')
    
    dir_path = os.path.dirname(fig_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    plt.savefig(fig_path)
    plt.close()