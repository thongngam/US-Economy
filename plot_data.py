"""
Plot US economic data from FRED.
Resamples all series to monthly resolution and generates charts.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

USREC_FILE = DATA_DIR / "usrec.csv"


def load_recessions() -> list[tuple[pd.Timestamp, pd.Timestamp]]:
    """Load US recession periods from USREC series (peak to trough)."""
    df = pd.read_csv(USREC_FILE)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    # Find contiguous runs of value == 1
    in_recession = df["value"] == 1
    recessions = []
    start = None
    for date, val in in_recession.items():
        if val and start is None:
            start = date
        elif not val and start is not None:
            recessions.append((start, date))
            start = None
    if start is not None:
        recessions.append((start, in_recession.index[-1]))
    return recessions


def shade_recessions(ax: plt.Axes, recessions: list[tuple[pd.Timestamp, pd.Timestamp]]):
    """Add gray shading for recession periods on an axes."""
    for start, end in recessions:
        ax.axvspan(start, end, color="gray", alpha=0.2, linewidth=0)

# (csv_filename, series_label, y_label, group, freq)
# freq: m=monthly, w=weekly, d=daily, q=quarterly, a=annual
SERIES = [
    ("cpi_urban_consumers.csv",      "CPI (All Items)",              "Index 1982-1984=100", "Inflation",     "m"),
    ("cpi_core.csv",                 "Core CPI (Less Food & Energy)","Index 1982-1984=100", "Inflation",     "m"),
    ("median_house_price.csv",       "Median House Price",           "$",                  "Housing",       "q"),
    ("case_shiller_hpi.csv",         "Case-Shiller HPI",             "Index Jan 2000=100", "Housing",       "m"),
    ("mortgage_rate_30yr.csv",       "30yr Mortgage Rate",           "%",                  "Housing",       "w"),
    ("federal_receipts.csv",         "Federal Receipts",             "$ Millions",          "Taxes",         "a"),
    ("federal_funds_rate.csv",       "Fed Funds Rate",               "%",                  "Monetary",      "m"),
    ("treasury_spread_10y2y.csv",    "10Y-2Y Treasury Spread",       "%",                  "Monetary",      "d"),
    ("gdp.csv",                      "GDP",                          "$ Billions",          "GDP",           "q"),
    ("real_gdp.csv",                 "Real GDP",                     "$ Billions (2017$)",  "GDP",           "q"),
    ("unemployment_rate.csv",        "Unemployment Rate",            "%",                  "Employment",    "m"),
    ("labor_participation.csv",      "Labor Force Participation",    "%",                  "Employment",    "m"),
    ("median_household_income.csv",  "Median Household Income",      "$",                  "Income",        "a"),
]

# Normalization ranges for overlay (min-max scaling)
NORM_RANGES = {
    "CPI (All Items)":              (0, 100),
    "Core CPI (Less Food & Energy)":(0, 100),
    "Median House Price":           (0, 100),
    "Case-Shiller HPI":             (0, 100),
    "30yr Mortgage Rate":           (0, 100),
    "Federal Receipts":             (0, 100),
    "Fed Funds Rate":               (0, 100),
    "10Y-2Y Treasury Spread":       (0, 100),
    "GDP":                          (0, 100),
    "Real GDP":                     (0, 100),
    "Unemployment Rate":            (0, 100),
    "Labor Force Participation":    (0, 100),
    "Median Household Income":      (0, 100),
}


def load_and_resample(csv_filename: str, freq: str = "m") -> pd.Series:
    """Load CSV and resample to monthly frequency.

    freq: original data frequency
      "m" = monthly (no resample needed)
      "w" = weekly (average to monthly)
      "d" = daily (average to monthly)
      "q" = quarterly (forward-fill to monthly)
      "a" = annual (forward-fill to monthly)
    """
    df = pd.read_csv(DATA_DIR / csv_filename)
    df["date"] = pd.to_datetime(df["date"])
    df = df.dropna(subset=["value"])
    df = df.set_index("date").sort_index()
    if freq in ("w", "d"):
        monthly = df["value"].resample("MS").mean()
    elif freq in ("q", "a"):
        monthly = df["value"].resample("MS").ffill()
    else:
        monthly = df["value"].resample("MS").mean()
    return monthly


def plot_individual(series: pd.Series, label: str, y_label: str, group: str,
                    recessions: list[tuple[pd.Timestamp, pd.Timestamp]]):
    """Create a single-series plot."""
    fig, ax = plt.subplots(figsize=(12, 5))
    shade_recessions(ax, recessions)
    ax.plot(series.index, series.values, linewidth=1.2, color="#1f77b4", zorder=3)
    ax.set_title(f"US Economy: {label}", fontsize=14, fontweight="bold")
    ax.set_ylabel(y_label)
    ax.set_xlabel("Date")
    # Clip x-axis: start 1960, end at data range
    ax.set_xlim(pd.Timestamp("1960-01-01"), series.index.max())
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    safe_name = label.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_").replace("&", "and")
    fig.savefig(PLOTS_DIR / f"{safe_name}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: {safe_name}.png")


def plot_overlay(all_series: dict[str, pd.Series],
                 recessions: list[tuple[pd.Timestamp, pd.Timestamp]]):
    """Create overlay plot with all series normalized to 0-100."""
    fig, axes = plt.subplots(4, 1, figsize=(14, 18), sharex=True)

    groups = {
        "Inflation": ["CPI (All Items)", "Core CPI (Less Food & Energy)"],
        "Housing": ["Median House Price", "Case-Shiller HPI", "30yr Mortgage Rate"],
        "Monetary": ["Fed Funds Rate", "10Y-2Y Treasury Spread"],
        "GDP & Employment": ["GDP", "Real GDP", "Unemployment Rate", "Labor Force Participation", "Median Household Income"],
    }

    colors = {
        "CPI (All Items)": "#e41a1c",
        "Core CPI (Less Food & Energy)": "#ff7f00",
        "Median House Price": "#377eb8",
        "Case-Shiller HPI": "#4daf4a",
        "30yr Mortgage Rate": "#984ea3",
        "Fed Funds Rate": "#a65628",
        "10Y-2Y Treasury Spread": "#f781bf",
        "GDP": "#999999",
        "Real GDP": "#66c2a5",
        "Unemployment Rate": "#fc8d62",
        "Labor Force Participation": "#8da0cb",
        "Median Household Income": "#e78ac3",
    }

    for ax, (group_name, series_names) in zip(axes, groups.items()):
        shade_recessions(ax, recessions)
        for name in series_names:
            if name in all_series:
                s = all_series[name].dropna()
                if s.empty:
                    continue
                # Normalize to 0-100
                smin, smax = s.min(), s.max()
                if smax == smin:
                    normalized = pd.Series(50, index=s.index)
                else:
                    normalized = (s - smin) / (smax - smin) * 100
                ax.plot(normalized.index, normalized.values, label=name,
                        linewidth=1.3, color=colors.get(name, None), zorder=3)
        ax.set_title(group_name, fontsize=12, fontweight="bold")
        ax.set_ylabel("Normalized (0-100)")
        ax.legend(loc="upper left", fontsize=8)
        ax.grid(True, alpha=0.3)

    # Clip x-axis: start 1960, end at data range
    all_max = max(s.index.max() for s in all_series.values() if not s.dropna().empty)
    axes[-1].set_xlim(pd.Timestamp("1960-01-01"), all_max)

    axes[-1].set_xlabel("Date")
    axes[-1].xaxis.set_major_locator(mdates.YearLocator(5))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    fig.suptitle("US Economy Dashboard — All Series (Normalized to 0-100)", fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(PLOTS_DIR / "overlay_all_series.png", dpi=150)
    plt.close(fig)
    print("  Saved: overlay_all_series.png")


def main():
    print("Loading recession periods...")
    recessions = load_recessions()
    print(f"  Found {len(recessions)} recession periods\n")

    print("Loading and resampling series to monthly resolution...\n")
    all_series = {}

    for csv_filename, label, y_label, group, freq in SERIES:
        monthly = load_and_resample(csv_filename, freq)
        all_series[label] = monthly
        print(f"  {label}: {len(monthly)} months ({monthly.index.min().date()} to {monthly.index.max().date()})")

    # Save merged monthly data
    merged_df = pd.DataFrame(all_series)
    merged_df.index.name = "date"
    merged_df.to_csv(DATA_DIR / "merged_monthly.csv")
    print(f"\nMerged monthly data saved: data/merged_monthly.csv ({len(merged_df)} rows, {len(merged_df.columns)} columns)")

    print("\nGenerating individual plots...")
    for csv_filename, label, y_label, group, freq in SERIES:
        plot_individual(all_series[label], label, y_label, group, recessions)

    print("\nGenerating overlay plot...")
    plot_overlay(all_series, recessions)

    print(f"\nDone. All plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
