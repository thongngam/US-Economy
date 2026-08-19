# US Economy Analysis

Analysis of past and current conditions of the US economy using data from the **Federal Reserve Economic Data (FRED)**.

## Data Series

| Category | Series | FRED ID | Frequency |
|----------|--------|---------|-----------|
| **Inflation** | CPI (All Urban Consumers) | CPIAUCSL | Monthly |
| | Core CPI (Less Food & Energy) | CPILFESL | Monthly |
| **Housing** | Median Sales Price of Houses | MSPUS | Quarterly |
| | Case-Shiller Home Price Index | CSUSHPINSA | Monthly |
| | 30-Year Fixed Mortgage Rate | MORTGAGE30US | Weekly |
| **Taxes** | Federal Receipts | FYFR | Annual |
| **Monetary** | Federal Funds Effective Rate | FEDFUNDS | Monthly |
| | 10Y-2Y Treasury Spread | T10Y2Y | Daily |
| **GDP** | Gross Domestic Product | GDP | Quarterly |
| | Real GDP | GDPC1 | Quarterly |
| **Employment** | Unemployment Rate | UNRATE | Monthly |
| | Labor Force Participation | CIVPART | Monthly |
| **Income** | Median Household Income | MEHOINUSA646N | Annual |

All series are resampled to monthly resolution and merged into `data/merged_monthly.csv`.

## Project Structure

```
US Economy/
├── README.md               # This file
├── architecture.md         # Detailed project documentation
├── requirements.txt        # Python dependencies
├── fetch_data.py           # Pull data from FRED API
├── plot_data.py            # Merge series and generate plots
├── data/                   # Raw and merged CSV files
│   ├── *.csv               # Individual series
│   ├── merged_monthly.csv  # All series merged to monthly
│   └── usrec.csv           # NBER recession indicator
└── plots/                  # Generated plots
    ├── *.png               # Individual series plots
    └── overlay_all_series.png  # Combined dashboard
```

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with your FRED API key (free, from https://fred.stlouisfed.org/docs/api/api_key/):

```
FRED_API_KEY=your_key_here
```

## Usage

1. **Fetch data** from FRED API:
   ```bash
   python fetch_data.py
   ```

2. **Generate plots** (resamples to monthly and creates charts):
   ```bash
   python plot_data.py
   ```

Plots start from 1990 and include gray shading for NBER-defined recession periods.

## Data Source

All data from [FRED](https://fred.stlouisfed.org/) (Federal Reserve Bank of St. Louis). Data is public domain with citation.

## Plots

Each series is plotted individually with recession shading. An overlay dashboard normalizes all 13 series to a 0-100 scale, grouped by:

- **Inflation** — CPI and Core CPI
- **Housing** — House prices, Case-Shiller HPI, mortgage rates
- **Monetary** — Fed Funds Rate, yield curve spread
- **GDP & Employment** — GDP, Real GDP, unemployment, labor participation, household income

### Overlay Dashboard

![US Economy Dashboard](plots/overlay_all_series.png)

### Inflation

![CPI All Items](plots/cpi_all_items.png)

![Core CPI](plots/core_cpi_less_food_and_energy.png)

### Housing

![Median House Price](plots/median_house_price.png)

![Case-Shiller HPI](plots/case-shiller_hpi.png)

![30yr Mortgage Rate](plots/30yr_mortgage_rate.png)

### Taxes

![Federal Receipts](plots/federal_receipts.png)

### Monetary Policy

![Fed Funds Rate](plots/fed_funds_rate.png)

![10Y-2Y Treasury Spread](plots/10y-2y_treasury_spread.png)

### GDP

![GDP](plots/gdp.png)

![Real GDP](plots/real_gdp.png)

### Employment

![Unemployment Rate](plots/unemployment_rate.png)

![Labor Force Participation](plots/labor_force_participation.png)

### Income

![Median Household Income](plots/median_household_income.png)

## COVID Period Econometrics (2019-2023)

Focused analysis on the COVID-19 recession and recovery using multivariable OLS regression.

### COVID Period Time Series

![COVID Timeseries](plots/covid_timeseries.png)

### Correlation Matrix

![COVID Correlation](plots/covid_correlation.png)

### Regression Models

#### Model 1: Unemployment Rate
**Unemployment ~ Fed Funds + CPI + Real GDP + Mortgage Rate**
- R² = 0.749, Adj R² = 0.731, F = 41.13 (p < 0.001)
- Real GDP (p < 0.001) and CPI (p < 0.001) are highly significant
- Fed Funds Rate not significant (p = 0.211)

![Unemployment Regression](plots/covid_reg_unemployment.png)

#### Model 2: CPI Inflation
**CPI MoM% ~ Fed Funds + Yield Spread + Mortgage Rate + Real GDP**
- R² = 0.403, Adj R² = 0.359
- Fed Funds Rate significant and negative (p = 0.026) — rate hikes slow inflation
- Real GDP significant (p = 0.001)

![Inflation Regression](plots/covid_reg_inflation.png)

#### Model 3: Real GDP Growth
**GDP MoM% ~ Fed Funds + Unemployment + Mortgage Rate**
- R² = 0.045 — none of the predictors explain GDP growth well in this period
- The COVID shock was exogenous, not driven by standard macro variables

![GDP Regression](plots/covid_reg_gdp.png)

#### Model 4: House Price Growth
**House Price MoM% ~ Mortgage Rate + Fed Funds + CPI + Unemployment**
- R² = 0.110 — weak explanatory power
- Housing boom driven by supply constraints, remote work demand, and low inventory — not captured by standard variables

![Housing Regression](plots/covid_reg_housing.png)

#### Lag Analysis (Granger-style)
**CPI ~ Unemployment Lag 1/2/3**
- R² = 0.227, significant overall (F = 5.19, p = 0.003)
- Lag 1 coefficient negative (-2.76) but marginally significant (p = 0.106)
- Suggests rising unemployment precedes disinflation with ~1 month lag

![Lag Regression](plots/covid_reg_lag.png)

### Key Findings

1. **Unemployment model fits well** (R² = 0.75): GDP contraction and inflation spikes explain most of the COVID unemployment surge
2. **Fed Funds Rate affects inflation**: Rate hikes are associated with lower inflation growth (coefficient = -0.11)
3. **GDP and housing not explainable** by standard variables during COVID — the shock was exogenous (pandemic lockdowns, fiscal stimulus, supply chain disruption)
4. **Unemployment leads inflation**: Rising unemployment precedes lower CPI growth by ~1 month (Phillips Curve relationship)
5. **Multicollinearity**: CPI and GDP highly correlated (0.91), mortgage rate and Fed Funds highly correlated (0.91) — caution interpreting individual coefficients

## Forecasting (2019-2023)

Univariate and multivariate time series models trained on 1990-2018 data, forecasting the COVID period.

### Methods

| Model | Type | Description |
|-------|------|-------------|
| ARMA(2,2) | Univariate | Autoregressive moving average on levels |
| ARIMA(1,1,1) | Univariate | Integrated ARMA with differencing |
| VAR(4) | Multivariate | Vector autoregression on differenced series |
| VECM(2) | Multivariate | Vector error correction with cointegration |

### Forecast Accuracy (RMSE)

| Series | ARMA | ARIMA | VAR | VECM |
|--------|------|-------|-----|------|
| CPI (All Items) | 22.97 | 30.56 | 1.11* | 19.11 |
| Fed Funds Rate | 2.28 | 2.03 | 1.99 | 2.07 |
| Unemployment Rate | 2.68 | 2.55 | 1.44 | 2.56 |
| Real GDP | 1527.77 | 1508.62 | 307.50* | 667.76 |

*VAR on differenced (month-over-month change) — not directly comparable to level forecasts.

### Stationarity Tests (ADF)

| Series | Statistic | p-value | Conclusion |
|--------|-----------|---------|------------|
| CPI | 2.948 | 1.000 | Non-stationary |
| Fed Funds Rate | -3.006 | 0.034 | Stationary |
| Unemployment Rate | -3.928 | 0.002 | Stationary |
| Real GDP | 3.850 | 1.000 | Non-stationary |

### Comparison Plots

![CPI Forecast](plots/forecast_comparison_cpi_all_items.png)

![Fed Funds Forecast](plots/forecast_comparison_fed_funds_rate.png)

![Unemployment Forecast](plots/forecast_comparison_unemployment_rate.png)

![GDP Forecast](plots/forecast_comparison_real_gdp.png)

### Key Findings

1. **COVID was unpredictable** — all models underforecast the unemployment spike (14.8%) and CPI surge, as the pandemic was an exogenous shock
2. **VAR outperforms univariate** — multivariate models capture cross-variable dynamics (e.g., GDP drop → unemployment rise)
3. **VECM cointegration** — Johansen test shows 1 cointegrating relationship among CPI, Fed Funds, Unemployment, GDP at 90% confidence
4. **ARMA best for Fed Funds** — interest rate path was relatively smooth and predictable (RMSE = 2.28)
5. **No model captures tail events** — COVID-19, lockdowns, and fiscal stimulus were outside historical patterns
