# viz_india.py
# generates 4 charts for the india article
# run from project root: python src/viz_india.py

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

# color palette - dark github-style theme
BG = "#0d1117"
WHITE = "#e6edf3"
GRAY = "#8b949e"
MGRAY  = "#30363d"
RED = "#f87171"
GREEN  = "#3fb950"
ORANGE = "#e3b341"
BLUE = "#60a5fa"


def style_axes(fig, ax):
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.tick_params(colors=GRAY, labelsize=9)
    ax.xaxis.label.set_color(GRAY)
    ax.yaxis.label.set_color(GRAY)
    for sp in ax.spines.values():
        sp.set_edgecolor(MGRAY)
    ax.grid(axis="y", color=MGRAY, lw=0.5, alpha=0.6)
    ax.grid(axis="x", color=MGRAY, lw=0.5, alpha=0.3)

def add_source(fig, txt):
    fig.text(0.98, 0.012, txt, ha="right", fontsize=7.5, color=GRAY)


# ---- chart 1: INR/USD ----

df_inr = pd.read_csv("data/processed/inr_usd.csv", parse_dates=["date"])
df_inr_m = df_inr.set_index("date").resample("ME").last().reset_index()

fig, ax = plt.subplots(figsize=(14, 6))
style_axes(fig, ax)

ax.plot(df_inr_m.date, df_inr_m.inr_per_usd, color=RED, lw=2.0, zorder=4)
ax.fill_between(df_inr_m.date, df_inr_m.inr_per_usd,
                df_inr_m.inr_per_usd.min(), alpha=0.12, color=RED, zorder=3)

events = [
    ("2016-11", 68.6, "Demonetisation\nNov 2016",      "2016-03", 74.0, "right"),
    ("2020-04", 76.2, "Covid crash\nApr 2020",          "2020-09", 79.5, "left"),
    ("2022-09", 81.9, "Fed hikes peak\nRupee hits ₹82", "2021-04", 86.5, "center"),
    ("2023-01", 82.7, "RBI burns\n$100B reserves",      "2024-02", 88.5, "left"),
]
for xy_dt, xy_y, label, txt_dt, txt_y, ha in events:
    ax.annotate(label,
        xy=(pd.Timestamp(xy_dt), xy_y),
        xytext=(pd.Timestamp(txt_dt), txt_y),
        fontsize=7.5, color=GRAY, ha=ha,
        arrowprops=dict(arrowstyle="-", color=MGRAY, lw=0.8))

ax.text(df_inr_m.date.iloc[0], df_inr_m.inr_per_usd.iloc[0] - 1.5,
        f"₹{df_inr_m.inr_per_usd.iloc[0]:.0f}", color=ORANGE,
        fontsize=10, fontweight="bold", ha="center")
ax.text(df_inr_m.date.iloc[-1] - pd.DateOffset(months=16),
        df_inr_m.inr_per_usd.iloc[-1] + 2.2,
        f"₹{df_inr_m.inr_per_usd.iloc[-1]:.0f}", color=RED,
        fontsize=10, fontweight="bold", ha="center")

pct_drop = (df_inr_m.inr_per_usd.iloc[-1] / df_inr_m.inr_per_usd.iloc[0] - 1) * 100
ax.text(0.38, 0.97, f"Rupee lost {pct_drop:.0f}% of its value\nagainst the dollar in 10 years",
        transform=ax.transAxes, ha="center", va="top",
        fontsize=10, color=RED, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1a0505", edgecolor=RED, alpha=0.9))

ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}"))
ax.set_ylabel("Rupees per 1 US Dollar  (higher = weaker rupee)")
ax.set_title("The Rupee Has Never Stopped Falling", color=WHITE, fontsize=14, fontweight="bold", pad=42)
ax.text(0.5, 1.025, "USD/INR exchange rate, 2015–2026  |  Every year: more rupees to buy the same dollar",
        transform=ax.transAxes, ha="center", fontsize=9, color=GRAY, style="italic")

add_source(fig, "Source: FRED (DEXINUS)")
plt.tight_layout()
plt.savefig("output/charts/ch1_inr.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("saved ch1_inr.png")


# ---- chart 2: LPG prices ----

df_lgp = pd.read_csv("data/processed/lgp_prices.csv", parse_dates=["date"])

fig, ax = plt.subplots(figsize=(14, 6))
style_axes(fig, ax)

ax.plot(df_lgp.date, df_lgp.lgp_price_inr,
        color=ORANGE, lw=2.2, marker="o", markersize=5, zorder=4)
ax.fill_between(df_lgp.date, df_lgp.lgp_price_inr, 0, alpha=0.10, color=ORANGE, zorder=3)

lgp_events = [
    ("2020-05", 581,  "Covid: oil crashes\nGovt passes savings", "2021-03", 490, "left"),
    ("2022-07", 1053, "Russia-Ukraine\nAll-time high ₹1,053",    "2022-07", 1113, "center"),
    ("2023-08", 903,  "Govt cuts ₹200\npre-election",            "2023-08", 813, "center"),
]
for dt, y, lbl, tdt, ty, ha in lgp_events:
    ax.annotate(lbl,
        xy=(pd.Timestamp(dt), y), xytext=(pd.Timestamp(tdt), ty),
        fontsize=8, color=GRAY, ha=ha,
        arrowprops=dict(arrowstyle="-", color=MGRAY, lw=0.8))

start_price = df_lgp.lgp_price_inr.iloc[0]
end_price = df_lgp.lgp_price_inr.iloc[-1]

ax.text(df_lgp.date.iloc[0], start_price - 70,
        f"₹{start_price:.0f}\n(2015)", color=GREEN, fontsize=10, fontweight="bold", ha="center")
ax.text(df_lgp.date.iloc[-1], end_price + 55,
        f"₹{end_price:.0f}\n(2025)", color=RED, fontsize=10, fontweight="bold", ha="center")

pct_lgp = (end_price / start_price - 1) * 100
ax.text(0.99, 0.97, f"+{pct_lgp:.0f}% in 10 years",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=11, color=ORANGE, fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.4", facecolor="#1a0e00", edgecolor=ORANGE, alpha=0.9))

ax.set_ylim(0, 1200)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:.0f}"))
ax.set_title("LPG Cylinder Price (14.2 kg, Delhi)", color=WHITE, fontsize=14, fontweight="bold", pad=42)
ax.text(0.5, 1.025, "What you pay at the gas agency, the number everyone has felt but nobody explains",
        transform=ax.transAxes, ha="center", fontsize=9, color=GRAY, style="italic")

add_source(fig, "Source: PPAC, Ministry of Petroleum  |  hand-curated public record")
plt.tight_layout()
plt.savefig("output/charts/ch2_lgp.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("saved ch2_lgp.png")


# chart 3 - brent in usd vs inr, dual axis
# this one has two y axes so the setup is a bit more annoying

df_oil = pd.read_csv("data/processed/oil_inr.csv", parse_dates=["date"])

fig, ax1 = plt.subplots(figsize=(14, 7))
style_axes(fig, ax1)
ax2 = ax1.twinx()
ax2.set_facecolor(BG)
ax2.tick_params(colors=GRAY, labelsize=9)
for sp in ax2.spines.values():
    sp.set_edgecolor(MGRAY)

l1, = ax1.plot(df_oil.date, df_oil.brent_usd, color=BLUE,   lw=1.8, label="Brent in USD (global price)")
l2, = ax2.plot(df_oil.date, df_oil.brent_inr, color=ORANGE, lw=2.0, label="Brent in INR (what India pays)")

ax1.set_ylabel("USD per barrel", color=BLUE)
ax2.set_ylabel("₹ per barrel  (INR cost)", color=ORANGE)
ax1.yaxis.label.set_color(BLUE)
ax2.yaxis.label.set_color(ORANGE)
ax1.tick_params(axis="y", colors=BLUE)
ax2.tick_params(axis="y", colors=ORANGE)

ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}"))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))

s = df_oil.iloc[0]
e = df_oil.iloc[-1]
ax1.text(0.02, 0.82,
         f"Global oil price: ${s.brent_usd:.0f} → ${e.brent_usd:.0f}/barrel  (+{(e.brent_usd/s.brent_usd-1)*100:.0f}%)\n"
         f"India's cost:  ₹{s.brent_inr:,.0f} → ₹{e.brent_inr:,.0f}/barrel  (+{(e.brent_inr/s.brent_inr-1)*100:.0f}%)",
         transform=ax1.transAxes, ha="left", va="top", fontsize=9.5, color=WHITE,
         bbox=dict(boxstyle="round,pad=0.45", facecolor="#0d1117", edgecolor=MGRAY, alpha=0.95))

ax1.set_title("The Double Hit: Oil Gets More Expensive Twice", color=WHITE, fontsize=14, fontweight="bold", pad=42)
ax1.text(0.5, 1.025, "Global oil prices go up AND the rupee weakens. India pays both hits at the same time.",
         transform=ax1.transAxes, ha="center", fontsize=9, color=GRAY, style="italic")

ax1.legend([l1, l2], [l1.get_label(), l2.get_label()],
           facecolor=BG, edgecolor=MGRAY, labelcolor=WHITE, fontsize=9, loc="lower right")

add_source(fig, "Source: FRED (DCOILBRENTEU, DEXINUS)")
plt.tight_layout()
plt.savefig("output/charts/ch3_oil_doublehit.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("saved ch3_oil_doublehit.png")


# ---- chart 4: trade balance ----

df_trade = pd.read_csv("data/processed/trade.csv")

years = df_trade.year.astype(int)
x = np.arange(len(years))
w = 0.38

fig, ax = plt.subplots(figsize=(13, 6))
style_axes(fig, ax)

ax.bar(x - w/2, df_trade.exports_bn, w, label="Exports (what India earns)", color=GREEN, alpha=0.85)
ax.bar(x + w/2, df_trade.imports_bn, w, label="Imports (what India spends)", color=RED, alpha=0.85)

ax2 = ax.twinx()
ax2.set_facecolor(BG)
ax2.tick_params(colors=GRAY, labelsize=9)
for sp in ax2.spines.values():
    sp.set_edgecolor(MGRAY)
ax2.plot(x, df_trade.balance_bn, color=ORANGE, lw=2.0,
         marker="o", markersize=5, zorder=5, label="Trade balance (gap)")
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.0f}B"))
ax2.set_ylabel("Trade balance (USD B)", color=ORANGE)
ax2.yaxis.label.set_color(ORANGE)
ax2.tick_params(axis="y", colors=ORANGE)

ax.set_xticks(x)
ax.set_xticklabels(years, color=GRAY, fontsize=9)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"${v:.0f}B"))
ax.set_ylabel("USD Billions")

worst = df_trade.balance_bn.idxmin()
ax2.annotate(f"−${abs(df_trade.balance_bn.iloc[worst]):.0f}B\n(worst gap)",
    xy=(worst, df_trade.balance_bn.iloc[worst]),
    xytext=(worst - 1.5, df_trade.balance_bn.iloc[worst] - 25),
    fontsize=8, color=ORANGE,
    arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1.0))

ax.set_title("India Has Never Exported More Than It Imports", color=WHITE, fontsize=14, fontweight="bold", pad=42)
ax.text(0.5, 1.025, "Every year, India spends more dollars buying from the world than it earns selling to it",
        transform=ax.transAxes, ha="center", fontsize=9, color=GRAY, style="italic")

l1, lb1 = ax.get_legend_handles_labels()
l2, lb2 = ax2.get_legend_handles_labels()
ax.legend(l1+l2, lb1+lb2, facecolor=BG, edgecolor=MGRAY, labelcolor=WHITE, fontsize=9, loc="upper left")

add_source(fig, "Source: World Bank (BX.GSR.GNFS.CD, BM.GSR.GNFS.CD)")
plt.tight_layout()
plt.savefig("output/charts/ch4_trade.png", dpi=150, bbox_inches="tight", facecolor=BG)
plt.close()
print("saved ch4_trade.png")

print("\ndone")
