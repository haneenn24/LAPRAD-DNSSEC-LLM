
# utils/graphs.py
import matplotlib.pyplot as plt

def bar_two_conditions(title, xlabels, series_a, series_b, label_a, label_b, ylabel, out_png):
    import numpy as np
    x = np.arange(len(xlabels))
    width = 0.35
    fig, ax = plt.subplots(figsize=(7,5))
    ax.bar(x - width/2, series_a, width, label=label_a)
    ax.bar(x + width/2, series_b, width, label=label_b)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, rotation=15)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_png, dpi=200)
    plt.close(fig)

def line_by_matrix(title, xvals, yvals, label, xlabel, ylabel, out_png):
    fig, ax = plt.subplots(figsize=(7,5))
    ax.plot(xvals, yvals, marker="o", label=label)
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel); ax.set_title(title)
    ax.grid(True, alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig(out_png, dpi=200); plt.close(fig)
