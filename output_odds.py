import numpy as np
import matplotlib.pyplot as plt
import os

def plot_odds(n_competetors, winners, fig_path):
    # Plot competetor win frequencies
    bins = np.arange(1, n_competetors + 1.5) - 0.5
    fig, ax = plt.subplots()
    _ = ax.hist(winners, bins)
    ax.set_xticks(bins + 0.5)

    dir_path = os.path.dirname(fig_path)

    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    plt.savefig(fig_path)
    plt.close()