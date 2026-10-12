"""House style shared by figures.py and castanet_md.py: palette, rcParams, helpers."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
import numpy as np

SURFACE = "#fcfcfb"; INK = "#0b0b0b"; SECOND = "#52514e"; MUTED = "#898781"
GRID = "#e1e0d9"; BASE = "#c3c2b7"; CRITICAL = "#d03b3b"; NAT = "#898781"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
    "font.family": "sans-serif", "text.color": INK,
    "axes.edgecolor": BASE, "axes.labelcolor": SECOND, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True,
    "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "axes.spines.top": False, "axes.spines.right": False, "font.size": 11,
})

HALO = [pe.withStroke(linewidth=2.6, foreground=SURFACE)]   # text over a basemap


def style(ax):
    ax.grid(axis="x", visible=False)
    ax.spines["left"].set_visible(False)
    ax.tick_params(length=0)
    loc = mdates.AutoDateLocator()
    ax.xaxis.set_major_locator(loc)
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(loc))


def arr(v):
    return np.array([np.nan if x is None else x for x in v], dtype=float)


def save(fig, path, colors=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=144, bbox_inches="tight")
    plt.close(fig)
    if colors:      # a truecolour basemap costs 750 kB, and every build commits one
        from PIL import Image
        Image.open(path).convert("RGB").quantize(
            colors=colors, dither=Image.Dither.NONE).save(path, optimize=True)
    print(f"wrote {path} ({os.path.getsize(path) // 1024} kB)")


def end_label(ax, x, y, text, color):
    ax.annotate(text, (x, y), xytext=(6, 0), textcoords="offset points",
                va="center", color=color, fontsize=10, fontweight="bold")
