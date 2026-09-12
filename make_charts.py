import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter

from pengueats import run_simulation

BG = "#0D1117"
TEXT = "#C9D1D9"
MUTED = "#8B949E"
BLUE = "#79C0FF"
GREEN = "#7EE787"
ORANGE = "#FFA657"
RED = "#FF7B72"
GRID = "#30363D"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["text.color"] = TEXT
plt.rcParams["axes.labelcolor"] = TEXT
plt.rcParams["xtick.color"] = MUTED
plt.rcParams["ytick.color"] = MUTED

inventory, finance, orders, suggester, learner, daily_orders = run_simulation()

daily_profit = finance.daily_profit()
dates = [d.strftime("%a %d") for d in daily_profit.keys()]
values = list(daily_profit.values())
cumulative = []
running = 0
for v in values:
    running += v
    cumulative.append(running)

fig, ax = plt.subplots(figsize=(9, 4.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.bar(dates, values, color=[RED if v < 0 else GREEN for v in values], width=0.55, label="Daily net")
ax2 = ax.twinx()
ax2.plot(dates, cumulative, color=BLUE, linewidth=3, marker="o", markersize=6, label="Cumulative profit")
ax.axhline(0, color=GRID, linewidth=0.8)
ax.set_ylabel("Daily net (fish-coins)", fontsize=11)
ax2.set_ylabel("Cumulative profit (fish-coins)", fontsize=11, color=BLUE)
ax.set_title("PenguEats: Week 1 Profit Tracking", fontsize=14, fontweight="bold", color=TEXT, fontfamily="monospace")
ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
ax2.set_facecolor(BG)
ax2.tick_params(colors=BLUE)
for spine in ax.spines.values():
    spine.set_color(GRID)
for spine in ax2.spines.values():
    spine.set_color(GRID)
lines, labels = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc="lower left", frameon=False, fontsize=9, labelcolor=TEXT)
plt.tight_layout()
plt.savefig("chart_profit.png", dpi=200, facecolor=BG)
plt.close()

snapshot = inventory.snapshot()
fig, ax = plt.subplots(figsize=(8, 4.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
names = list(snapshot.keys())
qty = list(snapshot.values())
bars = ax.bar(names, qty, color=BLUE, width=0.5)
for bar, q in zip(bars, qty):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, str(q),
            ha="center", fontsize=10, color=TEXT, fontweight="bold")
ax.set_title("Remaining Inventory: End of Week", fontsize=14, fontweight="bold", color=TEXT, fontfamily="monospace")
ax.set_ylabel("Units in stock", fontsize=11)
ax.grid(axis="y", color=GRID, linewidth=0.6, alpha=0.6)
for spine in ax.spines.values():
    spine.set_color(GRID)
plt.tight_layout()
plt.savefig("chart_inventory.png", dpi=200, facecolor=BG)
plt.close()

fish_counter = Counter()
for order in orders.order_history:
    for name, q in order.items.items():
        fish_counter[name] += q

fig, ax = plt.subplots(figsize=(8, 4.5))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
labels, counts = zip(*fish_counter.most_common())
colors = [ORANGE] + [BLUE] * (len(labels) - 1)
bars = ax.barh(labels, counts, color=colors)
ax.invert_yaxis()
ax.set_title("Most-Ordered Fish (Week 1)", fontsize=14, fontweight="bold", color=TEXT, fontfamily="monospace")
ax.set_xlabel("Units ordered", fontsize=11)
ax.grid(axis="x", color=GRID, linewidth=0.6, alpha=0.6)
for spine in ax.spines.values():
    spine.set_color(GRID)
plt.tight_layout()
plt.savefig("chart_preferences.png", dpi=200, facecolor=BG)
plt.close()

print("Charts written: chart_profit.png, chart_inventory.png, chart_preferences.png")
print(f"Total profit: {finance.total_profit():.2f}")
print(f"Total orders: {len(orders.order_history)}")
print("Fish counter:", fish_counter)