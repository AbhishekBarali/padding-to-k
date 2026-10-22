#!/usr/bin/env python3
"""Draw the README figures from the numbers the paper itself plots.

Reads paper/source/generated/fig_c2_points.tex, fig_c2_ticks.tex and tab_outcomes_rows.tex (written
by analysis/full_study.py), so the figures always show the paper's numbers, and writes a light and a
dark version of each to docs/figures/. Needs matplotlib, which the analysis does not:

    pip install matplotlib==3.11.2
    python tools/readme_figures.py
"""

import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "paper" / "source" / "generated"
OUT = ROOT / "docs" / "figures"

# Display names for the condition codes, as the paper's \cnd macro prints them (paper/source/main.tex).
CONDITIONS = {
    "none": "no count",
    "prose_up_to_k": 'prose "up to k"',
    "prose_exactly_k": 'prose "exactly k"',
    "max_k_shown": "shown maximum",
    "min_k_shown": "shown minimum",
    "min_k_shown_fewer_ok": '"fewer is fine"',
    "min_k_enforced": "enforced minimum",
    "min_k_escape": "N/A escape",
}

THEMES = {
    "light": {"fg": "#1f2328", "muted": "#59636e", "grid": "#d1d9e0", "bg": "#ffffff",
              "gpu": "#cf222e", "hosted": "#0969da",
              "stack": ["#cf222e", "#bf8700", "#1a7f37", "#afb8c1"]},
    "dark": {"fg": "#f0f6fc", "muted": "#9198a1", "grid": "#3d444d", "bg": "#0d1117",
             "gpu": "#ff7b72", "hosted": "#58a6ff",
             "stack": ["#ff7b72", "#d29922", "#3fb950", "#656c76"]},
}


def read_c2() -> list[tuple[str, float, float, float, bool]]:
    """(label, estimate, low, high, is_gpu) per model, top to bottom as in the paper's figure 2."""
    ticks = (GEN / "fig_c2_ticks.tex").read_text(encoding="utf-8")
    ys = [int(y) for y in re.search(r"ytick=\{([^}]*)\}", ticks).group(1).split(",")]
    labels = re.findall(r"\{([^{}]+)\}", re.search(r"yticklabels=\{(.*)\},\s*$", ticks, re.M).group(1))
    by_y = dict(zip(ys, labels))
    rows = []
    points = (GEN / "fig_c2_points.tex").read_text(encoding="utf-8")
    for block, is_gpu in zip(points.split(r"\addplot")[1:], (True, False)):
        for est, y, lo, hi in re.findall(
                r"\(([-\d.]+),(\d+)\)\s*-=\s*\(([\d.]+),0\)\s*\+=\s*\(([\d.]+),0\)", block):
            est = float(est)
            rows.append((by_y[int(y)], est, est - float(lo), est + float(hi), is_gpu))
    return rows


def read_outcomes() -> list[tuple[str, list[float]]]:
    """(condition, [padded, says short, short with no note, unreadable]) in the paper's order."""
    rows = []
    for line in (GEN / "tab_outcomes_rows.tex").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\s*\\cnd\{(.+?)\}\s*&(.*)\\\\", line)
        if m:
            code = m.group(1).replace("\\_", "_")
            rows.append((CONDITIONS[code], [float(v) for v in m.group(2).split("&")[:4]]))
    return rows


def style(ax, t) -> None:
    ax.set_facecolor(t["bg"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(t["grid"])
    ax.tick_params(colors=t["fg"], length=0, labelsize=10)
    ax.xaxis.label.set_color(t["fg"])


def headline(rows, t, path: Path) -> None:
    gpu = [r for r in rows if r[4]]
    hosted = [r for r in rows if not r[4]]
    order = gpu + [None] + hosted  # a gap between the two groups
    fig, ax = plt.subplots(figsize=(8, 6.4), dpi=200, facecolor=t["bg"])
    style(ax, t)
    labels = []
    for i, r in enumerate(reversed(order)):
        if r is None:
            labels.append("")
            continue
        name, est, lo, hi, is_gpu = r
        c = t["gpu"] if is_gpu else t["hosted"]
        ax.plot([lo, hi], [i, i], color=c, lw=2, solid_capstyle="round")
        ax.plot(est, i, "o", color=c, ms=7, mec=t["bg"], mew=1.2, zorder=3)
        ax.text(hi + 0.06, i, f"{est:+.2f}", va="center", fontsize=9, color=t["muted"])
        labels.append(name.replace(" (T)", "  · Together").replace(" (B)", "  · Bedrock"))
    ax.set_yticks(range(len(labels)), labels)
    ax.axvline(0, color=t["muted"], lw=1, ls=(0, (4, 3)))
    ax.grid(axis="x", color=t["grid"], lw=0.6)
    ax.set_axisbelow(True)
    ax.set_xlim(-1.3, 3.0)
    ax.set_xlabel("Entries added by a schema minimum (shown, not enforced) over no count\n"
                  "same document and model, documents with n < k, 95% bootstrap interval",
                  fontsize=10, labelpad=8)
    gap = len(hosted)
    ax.text(-1.25, gap + len(gpu) + 0.6, "8 open-weight models on one GPU", color=t["gpu"],
            fontsize=10, fontweight="bold", va="bottom")
    ax.text(-1.25, gap - 0.4, "hosted reference runs (not pooled)", color=t["hosted"],
            fontsize=10, fontweight="bold", va="bottom")
    ax.set_ylim(-0.7, len(labels) + 0.4)
    fig.tight_layout()
    fig.savefig(path, facecolor=t["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def outcomes(rows, t, path: Path) -> None:
    parts = ["padded", "says it is short", "short list, no note", "unreadable"]
    fig, ax = plt.subplots(figsize=(8, 4.4), dpi=200, facecolor=t["bg"])
    style(ax, t)
    names = [r[0] for r in rows][::-1]
    values = [r[1] for r in rows][::-1]
    left = [0.0] * len(rows)
    for j, (part, colour) in enumerate(zip(parts, t["stack"])):
        widths = [v[j] for v in values]
        ax.barh(names, widths, left=left, color=colour, height=0.66, label=part,
                edgecolor=t["bg"], linewidth=0.8)
        for i, (l, w) in enumerate(zip(left, widths)):
            if w >= 8:
                ax.text(l + w / 2, i, f"{w:.1f}%", ha="center", va="center", fontsize=8.5,
                        color="#ffffff" if j < 3 else t["fg"], fontweight="bold")
        left = [l + w for l, w in zip(left, widths)]
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100], ["0%", "25%", "50%", "75%", "100%"])
    ax.set_xlabel("Outputs on documents with fewer than k items (8 GPU models, k = 3 and 5)",
                  fontsize=10, labelpad=8)
    leg = ax.legend(ncols=4, loc="lower center", bbox_to_anchor=(0.42, 1.0), frameon=False,
                    fontsize=9.5, handlelength=1.1, columnspacing=1.4)
    for text in leg.get_texts():
        text.set_color(t["fg"])
    fig.tight_layout()
    fig.savefig(path, facecolor=t["bg"], bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    c2, outs = read_c2(), read_outcomes()
    assert len(c2) == 17 and len(outs) == 8, (len(c2), len(outs))
    for name, t in THEMES.items():
        headline(c2, t, OUT / f"headline-{name}.png")
        outcomes(outs, t, OUT / f"outcomes-{name}.png")
    print(f"wrote {len(THEMES) * 2} figures to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
