import matplotlib.pyplot as plt
import os
from datetime import datetime

PLOT_DIR = "media/plots"

def create_progress_chart(interviews):
    if not interviews:
        return None

    os.makedirs(PLOT_DIR, exist_ok=True)

    dates = []
    scores = []

    for i in interviews:
        dates.append(datetime.strptime(i["date"], "%Y-%m-%d %H:%M:%S"))
        scores.append(i["percentage"])

    plt.style.use("seaborn-v0_8-darkgrid")

    plt.figure(figsize=(8, 4))

    plt.plot(
        dates,
        scores,
        marker="o",
        linewidth=2,
        markersize=6,
        color="#4F46E5"
    )

    for x, y in zip(dates, scores):
        plt.text(x, y + 1, f"{y}%", ha='center', fontsize=9)

    plt.title("Progress of Your Interview Performance", fontsize=14, weight="bold")
    plt.xlabel("Date")
    plt.ylabel("Score %")
    plt.ylim(0, 100)

    plt.grid(True, linestyle="--", alpha=0.4)

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False)

    plt.xticks(rotation=30)
    plt.tight_layout()

    file_path = os.path.join(PLOT_DIR, f"stats_{int(datetime.now().timestamp())}.png")
    plt.savefig(file_path, dpi=150)
    plt.close()

    return file_path