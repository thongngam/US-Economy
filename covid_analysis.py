"""
COVID Period Economic Analysis (2019-2023)
Multivariable regression and basic econometrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_breusch_godfrey
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

START = "2019-01-01"
END = "2023-12-31"


def load_covid_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "merged_monthly.csv", index_col=0, parse_dates=True)
    return df.loc[START:END].copy()


def compute_correlation_matrix(df: pd.DataFrame, save_path: str):
    """Compute and plot correlation matrix for COVID period."""
    corr = df.corr()
    fig, ax = plt.subplots(figsize=(12, 10))
    cax = ax.matshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    fig.colorbar(cax, ax=ax, shrink=0.8)
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    labels = [c.replace(" ", "\n") for c in corr.columns]
    ax.set_xticklabels(labels, rotation=90, fontsize=7)
    ax.set_yticklabels(labels, fontsize=7)
    # Annotate cells
    for i in range(len(corr)):
        for j in range(len(corr)):
            val = corr.iloc[i, j]
            color = "white" if abs(val) > 0.5 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=6, color=color)
    ax.set_title("COVID Period (2019-2023) — Correlation Matrix", fontsize=13, fontweight="bold", pad=20)
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")
    return corr


def run_ols(y: pd.Series, X: pd.DataFrame, title: str):
    """Run OLS regression and print results."""
    X_const = sm.add_constant(X)
    model = sm.OLS(y, X_const).fit()
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")
    print(model.summary().tables[1])
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj R-squared: {model.rsquared_adj:.4f}")
    print(f"  F-statistic: {model.fvalue:.2f} (p={model.f_pvalue:.4e})")
    return model


def plot_regression_diagnostics(model, title: str, save_path: str):
    """Plot residual diagnostics: fitted vs actual, residual histogram, ACF, QQ."""
    fitted = model.fittedvalues
    residuals = model.resid

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    # 1. Fitted vs Actual
    ax = axes[0, 0]
    ax.plot(residuals.index, model.model.endog, label="Actual", linewidth=1.2)
    ax.plot(residuals.index, fitted, label="Fitted", linewidth=1.2, linestyle="--")
    ax.set_title("Fitted vs Actual")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Residuals vs Fitted
    ax = axes[0, 1]
    ax.scatter(fitted, residuals, s=15, alpha=0.7)
    ax.axhline(0, color="red", linestyle="--", linewidth=0.8)
    ax.set_xlabel("Fitted Values")
    ax.set_ylabel("Residuals")
    ax.set_title("Residuals vs Fitted")
    ax.grid(True, alpha=0.3)

    # 3. Residual histogram
    ax = axes[1, 0]
    ax.hist(residuals, bins=15, edgecolor="black", alpha=0.7)
    ax.set_title("Residual Distribution")
    ax.set_xlabel("Residual")
    ax.grid(True, alpha=0.3)

    # 4. Residual ACF
    ax = axes[1, 1]
    sm.graphics.tsa.plot_acf(residuals, lags=12, ax=ax)
    ax.set_title("Residual ACF")

    fig.suptitle(title, fontsize=12, fontweight="bold")
    fig.tight_layout()
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


def plot_covid_timeseries(df: pd.DataFrame, save_path: str):
    """Plot key COVID period variables with recession shading."""
    fig, axes = plt.subplots(5, 1, figsize=(14, 16), sharex=True)

    # Load recessions
    rec_df = pd.read_csv(DATA_DIR / "usrec.csv", index_col=0, parse_dates=True)
    rec_df = rec_df.loc[START:END]
    in_recession = rec_df["value"] == 1
    start_rec = None
    for date, val in in_recession.items():
        if val and start_rec is None:
            start_rec = date
        elif not val and start_rec is not None:
            for ax in axes:
                ax.axvspan(start_rec, date, color="gray", alpha=0.25, linewidth=0)
            start_rec = None

    series_config = [
        ("CPI (All Items)", "CPI", "#e41a1c"),
        ("Fed Funds Rate", "Fed Funds Rate (%)", "#a65628"),
        ("Unemployment Rate", "Unemployment Rate (%)", "#377eb8"),
        ("Real GDP", "Real GDP ($B, 2017$)", "#66c2a5"),
        ("Median House Price", "Median House Price ($)", "#984ea3"),
    ]

    for ax, (col, label, color) in zip(axes, series_config):
        ax.plot(df.index, df[col], linewidth=1.5, color=color)
        ax.set_ylabel(label, fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.set_title(label, fontsize=10, fontweight="bold")

    axes[-1].set_xlabel("Date")
    axes[-1].xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    axes[-1].xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))

    fig.suptitle("US Economy — COVID Period (2019-2023)", fontsize=14, fontweight="bold", y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.98])
    fig.savefig(save_path, dpi=150)
    plt.close(fig)
    print(f"  Saved: {save_path}")


def main():
    print("Loading COVID period data (2019-2023)...")
    df = load_covid_data()
    print(f"  {len(df)} months, {len(df.columns)} variables\n")

    print("Generating COVID period time series plot...")
    plot_covid_timeseries(df, PLOTS_DIR / "covid_timeseries.png")

    print("\nComputing correlation matrix...")
    corr = compute_correlation_matrix(df, PLOTS_DIR / "covid_correlation.png")

    # --- MODEL 1: Unemployment as function of other variables ---
    print("\n--- MODEL 1: Unemployment Rate ---")
    y_unemp = df["Unemployment Rate"]
    X_unemp = df[["Fed Funds Rate", "CPI (All Items)", "Real GDP", "30yr Mortgage Rate"]].dropna()
    y_unemp = y_unemp.loc[X_unemp.index]
    model1 = run_ols(y_unemp, X_unemp, "Unemployment Rate ~ Fed Funds + CPI + Real GDP + Mortgage Rate")
    plot_regression_diagnostics(model1, "Model 1: Unemployment Rate", PLOTS_DIR / "covid_reg_unemployment.png")

    # --- MODEL 2: Inflation (CPI) as function of monetary and real variables ---
    print("\n--- MODEL 2: CPI Inflation ---")
    # Use month-over-month change in CPI as inflation measure
    cpi_change = df["CPI (All Items)"].pct_change() * 100
    X_cpi = df[["Fed Funds Rate", "10Y-2Y Treasury Spread", "30yr Mortgage Rate", "Real GDP"]].copy()
    X_cpi["CPI_change"] = cpi_change
    X_cpi = X_cpi.dropna()
    y_cpi = X_cpi.pop("CPI_change")
    model2 = run_ols(y_cpi, X_cpi, "CPI Inflation (MoM %) ~ Fed Funds + Yield Spread + Mortgage Rate + Real GDP")
    plot_regression_diagnostics(model2, "Model 2: CPI Inflation", PLOTS_DIR / "covid_reg_inflation.png")

    # --- MODEL 3: Real GDP growth ---
    print("\n--- MODEL 3: Real GDP ---")
    gdp_growth = df["Real GDP"].pct_change() * 100
    X_gdp = df[["Fed Funds Rate", "Unemployment Rate", "30yr Mortgage Rate"]].copy()
    X_gdp["GDP_growth"] = gdp_growth
    X_gdp = X_gdp.dropna()
    y_gdp = X_gdp.pop("GDP_growth")
    model3 = run_ols(y_gdp, X_gdp, "Real GDP Growth (MoM %) ~ Fed Funds + Unemployment + Mortgage Rate")
    plot_regression_diagnostics(model3, "Model 3: Real GDP Growth", PLOTS_DIR / "covid_reg_gdp.png")

    # --- MODEL 4: Housing prices ---
    print("\n--- MODEL 4: Median House Price ---")
    house_growth = df["Median House Price"].pct_change() * 100
    X_house = df[["30yr Mortgage Rate", "Fed Funds Rate", "CPI (All Items)", "Unemployment Rate"]].copy()
    X_house["House_growth"] = house_growth
    X_house = X_house.dropna()
    y_house = X_house.pop("House_growth")
    model4 = run_ols(y_house, X_house, "House Price Growth (MoM %) ~ Mortgage Rate + Fed Funds + CPI + Unemployment")
    plot_regression_diagnostics(model4, "Model 4: House Price Growth", PLOTS_DIR / "covid_reg_housing.png")

    # --- Granger-style lag analysis ---
    print("\n--- LAG ANALYSIS: Unemployment leading CPI ---")
    lag_df = df[["Unemployment Rate", "CPI (All Items)"]].copy()
    for lag in [1, 2, 3]:
        lag_df[f"Unemp_lag{lag}"] = lag_df["Unemployment Rate"].shift(lag)
    lag_df = lag_df.dropna()
    y_lag = lag_df["CPI (All Items)"]
    X_lag = lag_df[["Unemp_lag1", "Unemp_lag2", "Unemp_lag3"]]
    model_lag = run_ols(y_lag, X_lag, "CPI ~ Unemployment Lag 1/2/3 (Granger-style)")
    plot_regression_diagnostics(model_lag, "Lag Model: CPI ~ Unemployment Lags", PLOTS_DIR / "covid_reg_lag.png")

    print(f"\nDone. All plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
