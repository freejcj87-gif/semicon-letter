"""사이클 차트: 연간 영업이익 막대 + 주가 고점 시점 표시."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

plt.rcParams["font.family"] = "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), dpi=150)

cycles = [
    {
        "title": "2017 사이클",
        "years": [2016, 2017, 2018, 2019],
        "samsung": [29.2, 53.7, 58.9, 27.8],
        "hynix": [3.3, 13.7, 20.8, 2.7],
        "peak_x": 2017.84,
        "peak_label": "삼성 주가 고점\n('17.11)",
        "note": "실적 고점 '18 → 주가는 10~11개월 먼저",
    },
    {
        "title": "2020 사이클",
        "years": [2020, 2021, 2022, 2023],
        "samsung": [36.0, 51.6, 43.4, 6.6],
        "hynix": [5.0, 12.4, 6.8, -7.7],
        "peak_x": 2021.03,
        "peak_label": "삼성 주가 고점\n('21.01)",
        "note": "실적 고점 '21 → '23 적자 전환",
    },
]

for ax, c in zip(axes, cycles):
    w = 0.36
    xs = c["years"]
    b1 = ax.bar([x - w / 2 for x in xs], c["samsung"], width=w, color="#4a7fb5", label="삼성전자 영업이익")
    b2 = ax.bar([x + w / 2 for x in xs], c["hynix"], width=w, color="#8ab6d6", label="SK하이닉스 영업이익")
    ax.axvline(c["peak_x"], color="#c0392b", linestyle="--", linewidth=1.6)
    ymax = max(c["samsung"]) * 1.28
    ax.annotate(c["peak_label"], xy=(c["peak_x"], ymax * 0.82), fontsize=9.5,
                color="#c0392b", ha="left", va="top", xytext=(c["peak_x"] + 0.07, ymax * 0.97))
    ax.axhline(0, color="#999", linewidth=0.8)
    ax.set_title(f"{c['title']} — {c['note']}", fontsize=11)
    ax.set_xticks(xs)
    ax.set_ylim(min(0, min(c["hynix"])) * 1.4, ymax)
    ax.set_ylabel("연간 영업이익 (조원)", fontsize=9)
    ax.tick_params(labelsize=9)
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)

axes[0].legend(fontsize=9, loc="upper left", frameon=False)
fig.suptitle("주가 고점(빨간 점선)은 매번 실적 고점보다 먼저 왔다", fontsize=13, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.93])
fig.savefig("cycle_chart.png", bbox_inches="tight")
print("saved")
