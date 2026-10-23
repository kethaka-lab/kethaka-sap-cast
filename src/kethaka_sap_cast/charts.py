# Charts of benchmark results, saved as PNG for slides and reports.
import matplotlib

matplotlib.use("Agg")   # draw to files only, no pop-up windows
import matplotlib.pyplot as plt
import pandas as pd

# One line per model: MAPE for 1..7 days ahead.
def plot_error_by_days_ahead(by_horizon: pd.DataFrame, path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    for name in by_horizon.columns:
        ax.plot(by_horizon.index, by_horizon[name], marker="o", label=name)
    ax.set(title="Forecast error by days ahead (rolling backtest, Apr-Dec 2025)",
           xlabel="days ahead", ylabel="MAPE (%)")
    ax.legend()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# Actual sap for the last `days` days, with each weekly forecast overlaid.
def plot_recent_forecasts(data: pd.DataFrame, all_results: dict, names: list[str],
                          path, days: int = 42) -> None:
    start = data["date"].max() - pd.Timedelta(days=days)
    recent = data[data["date"] >= start]

    fig, ax = plt.subplots(figsize=(11, 4))
    ax.plot(recent["date"], recent["total_l"], color="black", lw=2, label="actual")
    not_tapped = recent[~recent["is_complete"]]
    ax.scatter(not_tapped["date"], not_tapped["total_l"], color="grey", zorder=3,
               label="tapper did not tap (not scored)")

    colours = ["tab:blue", "tab:orange", "tab:green", "tab:red", "tab:purple"]
    for name, colour in zip(names, colours):
        res = all_results[name]
        res = res[res["date"] >= start]
        for i, (_, week) in enumerate(res.groupby("cutoff")):
            ax.plot(week["date"], week["predicted"], color=colour, lw=1.5,
                    label=name if i == 0 else None)
    ax.set(title="7-day forecasts vs actual sap, last 6 weeks of 2025", ylabel="litres per day")
    ax.legend(loc="lower left")
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)