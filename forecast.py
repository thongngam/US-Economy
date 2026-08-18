"""
Economic Forecasting — ARMA, ARIMA, VAR, VECM
Forecast key US economic series from COVID period data.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import warnings
from pathlib import Path
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import VECM, coint_johansen
from statsmodels.tsa.stattools import adfuller

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).parent / "data"
PLOTS_DIR = Path(__file__).parent / "plots"
PLOTS_DIR.mkdir(exist_ok=True)

# Full history for training, COVID period for forecast evaluation
TRAIN_START = "1990-01-01"
TRAIN_END = "2018-12-31"
FORECAST_START = "2019-01-01"
FORECAST_END = "2023-12-31"
HORIZON = 60  # 60 months ahead


def load_monthly_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "merged_monthly.csv", index_col=0, parse_dates=True)
    return df


def adf_test(series, name):
    result = adfuller(series.dropna(), autolag="AIC")
    print(f"  ADF({name}): stat={result[0]:.3f}, p={result[1]:.4f} {'stationary' if result[1] < 0.05 else 'non-stationary'}")
    return result[1] < 0.05


def difference(series):
    return series.diff().dropna()


def plot_forecast(train, actual, forecast, title, filename, ci_lower=None, ci_upper=None):
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(train.index[-24:], train.values[-24:], label="Training Data", color="#1f77b4", linewidth=1.2)
    ax.plot(actual.index, actual.values, label="Actual", color="black", linewidth=1.5)
    ax.plot(forecast.index, forecast.values, label="Forecast", color="#e41a1c", linewidth=1.5, linestyle="--")
    if ci_lower is not None and ci_upper is not None:
        ax.fill_between(forecast.index, ci_lower.values, ci_upper.values, color="#e41a1c", alpha=0.15, label="95% CI")
    ax.axvline(actual.index[0], color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel("Date")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / filename, dpi=150)
    plt.close(fig)
    print(f"  Saved: {filename}")


# ──────────────────────────────────────────────
# ARMA / ARIMA
# ──────────────────────────────────────────────
def forecast_arma(series, name, order=(1, 0, 1)):
    train = series.loc[TRAIN_START:TRAIN_END]
    actual = series.loc[FORECAST_START:FORECAST_END]

    model = ARIMA(train, order=order)
    fitted = model.fit()
    pred = fitted.get_forecast(steps=HORIZON)
    forecast_mean = pred.predicted_mean
    forecast_mean.index = actual.index
    ci = pred.conf_int(alpha=0.05)
    ci.index = actual.index

    rmse = np.sqrt(((forecast_mean.values - actual.values) ** 2).mean())
    mae = np.abs(forecast_mean.values - actual.values).mean()
    print(f"  {name} ARMA{order}: RMSE={rmse:.3f}, MAE={mae:.3f}")

    plot_forecast(train, actual, forecast_mean,
                  f"{name} — ARMA{order} Forecast",
                  f"forecast_arma_{name.lower().replace(' ', '_')}.png",
                  ci.iloc[:, 0], ci.iloc[:, 1])
    return fitted


def forecast_arima(series, name, order=(1, 1, 1)):
    train = series.loc[TRAIN_START:TRAIN_END]
    actual = series.loc[FORECAST_START:FORECAST_END]

    model = ARIMA(train, order=order)
    fitted = model.fit()
    pred = fitted.get_forecast(steps=HORIZON)
    forecast_mean = pred.predicted_mean
    forecast_mean.index = actual.index
    ci = pred.conf_int(alpha=0.05)
    ci.index = actual.index

    rmse = np.sqrt(((forecast_mean.values - actual.values) ** 2).mean())
    mae = np.abs(forecast_mean.values - actual.values).mean()
    print(f"  {name} ARIMA{order}: RMSE={rmse:.3f}, MAE={mae:.3f}")

    plot_forecast(train, actual, forecast_mean,
                  f"{name} — ARIMA{order} Forecast",
                  f"forecast_arima_{name.lower().replace(' ', '_')}.png",
                  ci.iloc[:, 0], ci.iloc[:, 1])
    return fitted


# ──────────────────────────────────────────────
# VAR
# ──────────────────────────────────────────────
def forecast_var(df, var_names, maxlags=4):
    data = df[var_names].dropna()
    train = data.loc[TRAIN_START:TRAIN_END]
    actual = data.loc[FORECAST_START:FORECAST_END]

    # Check stationarity and difference if needed
    diff_needed = []
    for col in var_names:
        if not adf_test(train[col], col):
            diff_needed.append(col)

    if diff_needed:
        print(f"  Differencing non-stationary: {diff_needed}")
        for col in diff_needed:
            train[col] = train[col].diff()
            actual[col] = actual[col].diff()
        train = train.dropna()
        actual = actual.dropna()

    model = VAR(train)
    results = model.fit(maxlags=maxlags, ic="aic")
    print(f"\n  VAR lag order selected: {results.k_ar}")
    print(results.summary())

    lag_order = results.k_ar
    forecast_input = train.values[-lag_order:]
    forecast = results.forecast(forecast_input, steps=HORIZON)

    forecast_idx = pd.date_range(FORECAST_START, periods=HORIZON, freq="MS")
    forecast_df = pd.DataFrame(forecast, index=forecast_idx, columns=var_names)

    # Plot each variable
    for col in var_names:
        n = min(len(forecast_df), len(actual))
        rmse = np.sqrt(((forecast_df[col].values[:n] - actual[col].values[:n]) ** 2).mean())
        mae = np.abs(forecast_df[col].values[:n] - actual[col].values[:n]).mean()
        print(f"  VAR {col}: RMSE={rmse:.3f}, MAE={mae:.3f}")

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(train.index[-24:], train[col].values[-24:], label="Training", color="#1f77b4", linewidth=1.2)
        ax.plot(actual.index[:n], actual[col].values[:n], label="Actual", color="black", linewidth=1.5)
        ax.plot(forecast_df.index[:n], forecast_df[col].values[:n], label="VAR Forecast", color="#ff7f00", linewidth=1.5, linestyle="--")
        ax.axvline(actual.index[0], color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
        ax.set_title(f"{col} — VAR Forecast", fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        safe = col.lower().replace(" ", "_").replace("(", "").replace(")", "")
        fig.savefig(PLOTS_DIR / f"forecast_var_{safe}.png", dpi=150)
        plt.close(fig)
        print(f"  Saved: forecast_var_{safe}.png")

    return results, forecast_df


# ──────────────────────────────────────────────
# VECM
# ──────────────────────────────────────────────
def forecast_vecm(df, var_names, coint_rank=1, lag_order=2):
    data = df[var_names].dropna()
    train = data.loc[TRAIN_START:TRAIN_END]
    actual = data.loc[FORECAST_START:FORECAST_END]

    # Johansen cointegration test
    print("\n  Johansen Cointegration Test:")
    johansen = coint_johansen(train, det_order=0, k_ar_diff=lag_order)
    print(f"    Trace statistic: {johansen.lr1}")
    print(f"    Critical values (90%, 95%, 99%):")
    print(f"    {johansen.cvt}")

    model = VECM(train, k_ar_diff=lag_order, coint_rank=coint_rank, deterministic="ci")
    fitted = model.fit()
    print(f"\n  VECM fitted with cointegration rank={coint_rank}, lag={lag_order}")

    # Forecast
    forecast, lower, upper = predicted = fitted.predict(steps=HORIZON, alpha=0.05)
    forecast_df = pd.DataFrame(forecast, index=actual.index, columns=var_names)
    lower_df = pd.DataFrame(lower, index=actual.index, columns=var_names)
    upper_df = pd.DataFrame(upper, index=actual.index, columns=var_names)

    for col in var_names:
        rmse = np.sqrt(((forecast_df[col].values - actual[col].values) ** 2).mean())
        mae = np.abs(forecast_df[col].values - actual[col].values).mean()
        print(f"  VECM {col}: RMSE={rmse:.3f}, MAE={mae:.3f}")

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(train.index[-24:], train[col].values[-24:], label="Training", color="#1f77b4", linewidth=1.2)
        ax.plot(actual.index, actual[col].values, label="Actual", color="black", linewidth=1.5)
        ax.plot(forecast_df.index, forecast_df[col].values, label="VECM Forecast", color="#4daf4a", linewidth=1.5, linestyle="--")
        ax.fill_between(forecast_df.index, lower_df[col].values, upper_df[col].values, color="#4daf4a", alpha=0.15, label="95% CI")
        ax.axvline(actual.index[0], color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
        ax.set_title(f"{col} — VECM Forecast", fontsize=13, fontweight="bold")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        safe = col.lower().replace(" ", "_").replace("(", "").replace(")", "")
        fig.savefig(PLOTS_DIR / f"forecast_vecm_{safe}.png", dpi=150)
        plt.close(fig)
        print(f"  Saved: forecast_vecm_{safe}.png")

    return fitted, forecast_df


# ──────────────────────────────────────────────
# Comparison plot
# ──────────────────────────────────────────────
def plot_comparison(series, name, arma_fc, arima_fc, var_fc=None, vecm_fc=None):
    train = series.loc[TRAIN_START:TRAIN_END]
    actual = series.loc[FORECAST_START:FORECAST_END]
    forecast_idx = pd.date_range(FORECAST_START, periods=HORIZON, freq="MS")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(train.index[-24:], train.values[-24:], label="Training", color="#1f77b4", linewidth=1)
    ax.plot(actual.index, actual.values, label="Actual", color="black", linewidth=1.5)
    ax.plot(arma_fc.index, arma_fc.values, label="ARMA", color="#e41a1c", linewidth=1.2, linestyle="--")
    ax.plot(arima_fc.index, arima_fc.values, label="ARIMA", color="#ff7f00", linewidth=1.2, linestyle="--")
    if var_fc is not None:
        ax.plot(var_fc.index, var_fc.values, label="VAR", color="#984ea3", linewidth=1.2, linestyle="--")
    if vecm_fc is not None:
        ax.plot(vecm_fc.index, vecm_fc.values, label="VECM", color="#4daf4a", linewidth=1.2, linestyle="--")
    ax.axvline(actual.index[0], color="gray", linestyle=":", linewidth=0.8, alpha=0.7)
    ax.set_title(f"{name} — All Forecasts Comparison", fontsize=13, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    safe = name.lower().replace(" ", "_").replace("(", "").replace(")", "")
    fig.savefig(PLOTS_DIR / f"forecast_comparison_{safe}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: forecast_comparison_{safe}.png")


def main():
    print("Loading data...")
    df = load_monthly_data()
    print(f"  {len(df)} months, {len(df.columns)} variables\n")

    # --- ADF Tests ---
    print("=== Stationarity Tests (ADF) ===")
    test_cols = ["CPI (All Items)", "Fed Funds Rate", "Unemployment Rate", "Real GDP"]
    for col in test_cols:
        adf_test(df[col].dropna(), col)

    # --- ARMA / ARIMA on individual series ---
    print("\n=== ARMA Forecasts ===")
    arma_models = {}
    for col in test_cols:
        arma_models[col] = forecast_arma(df[col], col, order=(2, 0, 2))

    print("\n=== ARIMA Forecasts ===")
    arima_models = {}
    for col in test_cols:
        arima_models[col] = forecast_arima(df[col], col, order=(1, 1, 1))

    # --- VAR ---
    print("\n=== VAR Forecast ===")
    var_names = ["CPI (All Items)", "Fed Funds Rate", "Unemployment Rate", "Real GDP"]
    var_results, var_forecast = forecast_var(df, var_names, maxlags=4)

    # --- VECM ---
    print("\n=== VECM Forecast ===")
    vecm_results, vecm_forecast = forecast_vecm(df, var_names, coint_rank=1, lag_order=2)

    # --- Comparison plots ---
    print("\n=== Comparison Plots ===")
    forecast_idx = pd.date_range(FORECAST_START, periods=HORIZON, freq="MS")
    for col in test_cols:
        arma_pred = arma_models[col].get_forecast(steps=HORIZON).predicted_mean
        arma_pred.index = forecast_idx
        arima_pred = arima_models[col].get_forecast(steps=HORIZON).predicted_mean
        arima_pred.index = forecast_idx
        plot_comparison(
            df[col], col,
            arma_fc=arma_pred,
            arima_fc=arima_pred,
            var_fc=var_forecast[col] if col in var_forecast.columns else None,
            vecm_fc=vecm_forecast[col] if col in vecm_forecast.columns else None,
        )

    print(f"\nDone. All plots saved to: {PLOTS_DIR}")


if __name__ == "__main__":
    main()
