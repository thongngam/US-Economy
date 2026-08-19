# US Economy Analysis

## Project Overview

Analysis of past and current conditions of the US economy using data from **Federal Reserve Economic Data (FRED)**.

## Data Sources

All data pulled from: https://fred.stlouisfed.org/

## Data Series

### Inflation

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `CPIAUCSL` | Consumer Price Index for All Urban Consumers: All Items | Index 1982-1984=100 | Monthly | 332.813 | Jul 2026 |
| `CPILFESL` | CPI for All Urban Consumers: All Items Less Food and Energy | Index 1982-1984=100 | Monthly | 336.789 | Jul 2026 |

**Source:** U.S. Bureau of Labor Statistics
**Description:** The CPI is a measure of the average change over time in the prices paid by urban consumers for a market basket of consumer goods and services. CPIAUCSL includes ~88% of total population. CPILFESL (Core CPI) excludes volatile food and energy prices, making it the preferred measure for underlying inflation trends.

### Housing

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `MSPUS` | Median Sales Price of Houses Sold for the United States | Dollars | Quarterly | $410,700 | Q2 2026 |
| `CSUSHPINSA` | S&P CoreLogic Case-Shiller U.S. National Home Price Index | Index Jan 2000=100 | Monthly | 335.104 | May 2026 |
| `MORTGAGE30US` | 30-Year Fixed Rate Mortgage Average in the United States | Percent | Weekly | 6.67% | Aug 2026 |

**Sources:** U.S. Census Bureau, HUD, Freddie Mac, S&P Dow Jones Indices
**Description:**
- MSPUS tracks the median sale price of new houses sold, providing a direct measure of housing costs
- CSUSHPINSA is a repeat-sales index tracking changes in home values across 20+ metro areas
- MORTGAGE30US is the primary benchmark for mortgage lending rates, directly impacting housing affordability

### Taxes / Federal Revenue

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `FYFR` | Federal Receipts | Millions of Dollars | Annual (Fiscal Year) | $5,236,421 | FY2025 |

**Source:** U.S. Office of Management and Budget
**Description:** Total federal government receipts including individual income taxes, social insurance contributions, corporate income taxes, and other revenue sources.

### Monetary Policy / Interest Rates

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `FEDFUNDS` | Federal Funds Effective Rate | Percent | Monthly | 3.63% | Jul 2026 |
| `T10Y2Y` | 10-Year Treasury Constant Maturity Minus 2-Year | Percent | Daily | 0.51% | Aug 2026 |

**Source:** Board of Governors of the Federal Reserve System
**Description:**
- FEDFUNDS is the overnight lending rate between depository institutions, the primary tool of monetary policy
- T10Y2Y (yield curve spread) is a key recession predictor; inversions (negative values) have preceded every recession since 1955

### GDP / Economic Output

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `GDP` | Gross Domestic Product | Billions of Dollars, SAAR | Quarterly | $32,475.21B | Q2 2026 |
| `GDPC1` | Real Gross Domestic Product | Billions of Chained 2017 Dollars, SAAR | Quarterly | $24,270.6B | Q2 2026 |

**Source:** U.S. Bureau of Economic Analysis
**Description:** GDP is the total market value of all final goods and services produced within the US. Real GDP (GDPC1) is inflation-adjusted, providing a true measure of economic growth.

### Employment

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `UNRATE` | Unemployment Rate | Percent, Seasonally Adjusted | Monthly | 4.1% | Jul 2026 |
| `CIVPART` | Labor Force Participation Rate | Percent, Seasonally Adjusted | Monthly | 61.4% | Jul 2026 |

**Source:** U.S. Bureau of Labor Statistics
**Description:**
- UNRATE (U-3) is the official unemployment rate, measuring the percentage of the labor force that is jobless and actively seeking employment
- CIVPART measures the percentage of the civilian noninstitutional population that is working or actively looking for work

### Income

| Series ID | Name | Units | Frequency | Latest Value | Updated |
|-----------|------|-------|-----------|--------------|---------|
| `MEHOINUSA646N` | Median Household Income in the United States | Dollars | Annual | $83,730 | 2024 |

**Source:** U.S. Census Bureau
**Description:** Median household income provides a measure of the purchasing power and standard of living for the typical American household.

## Project Structure

```
US Economy/
├── README.md                          # Project overview, usage, results
├── architecture.md                    # This file - project documentation
├── requirements.txt                   # Python dependencies
├── fetch_data.py                      # Script to pull data from FRED API
├── plot_data.py                       # Merge series to monthly, generate plots
├── covid_analysis.py                  # COVID period (2019-2023) econometrics
├── forecast.py                        # ARMA/ARIMA/VAR/VECM forecasting
├── .env                               # FRED API key (not committed)
├── data/
│   ├── cpi_urban_consumers.csv          # CPIAUCSL (monthly)
│   ├── cpi_core.csv                     # CPILFESL (monthly)
│   ├── median_house_price.csv           # MSPUS (quarterly)
│   ├── case_shiller_hpi.csv             # CSUSHPINSA (monthly)
│   ├── mortgage_rate_30yr.csv           # MORTGAGE30US (weekly)
│   ├── federal_receipts.csv             # FYFR (annual)
│   ├── federal_funds_rate.csv           # FEDFUNDS (monthly)
│   ├── treasury_spread_10y2y.csv        # T10Y2Y (daily)
│   ├── gdp.csv                          # GDP (quarterly)
│   ├── real_gdp.csv                     # GDPC1 (quarterly)
│   ├── unemployment_rate.csv            # UNRATE (monthly)
│   ├── labor_participation.csv          # CIVPART (monthly)
│   ├── median_household_income.csv      # MEHOINUSA646N (annual)
│   ├── usrec.csv                        # USREC NBER recession indicator (monthly)
│   └── merged_monthly.csv               # All series merged to monthly resolution
└── plots/
    ├── *.png                            # 13 individual series plots
    ├── overlay_all_series.png           # 4-panel normalized dashboard
    ├── covid_timeseries.png             # COVID period variable panels
    ├── covid_correlation.png            # Correlation matrix
    ├── covid_reg_*.png                  # 4 OLS models + lag analysis diagnostics
    └── forecast_*.png                   # ARMA/ARIMA/VAR/VECM forecasts + comparisons
```

## Data Processing

All raw series are resampled to **monthly resolution**:
- Daily/weekly series (T10Y2Y, MORTGAGE30US): averaged by calendar month
- Quarterly/annual series: forward-filled to monthly (value held constant until next observation)
- The merged dataset is saved as `data/merged_monthly.csv`

## API Access

- **Provider:** Federal Reserve Bank of St. Louis (FRED)
- **API Key:** Configured in `.env` or passed to fetch script
- **Rate Limit:** 120 requests per minute
- **Documentation:** https://fred.stlouisfed.org/docs/api/fred/

## Data Retrieval Notes

- Direct CSV download URLs available at: `https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}`
- API endpoint: `https://api.stlouisfed.org/fred/series/observations?series_id={SERIES_ID}&api_key={KEY}&file_type=json`
- All data is public domain and free to use with citation

## Plots

### Individual Series
Each series is plotted separately with its native units on the y-axis and date on the x-axis. Files saved to `plots/`.

### Overlay Dashboard
All 13 series are normalized to a 0-100 scale (min-max normalization) and grouped into 4 panels:
- **Inflation:** CPI (All Items), Core CPI
- **Housing:** Median House Price, Case-Shiller HPI, 30yr Mortgage Rate
- **Monetary:** Fed Funds Rate, 10Y-2Y Treasury Spread
- **GDP & Employment:** GDP, Real GDP, Unemployment Rate, Labor Force Participation, Median Household Income

## Key Relationships to Analyze

1. **Inflation vs Interest Rates:** Fed raises rates to combat inflation
2. **Mortgage Rates vs Home Prices:** Higher rates typically cool housing prices
3. **Unemployment vs GDP:** Okun's Law - inverse relationship
4. **Yield Curve vs Recession:** Inversion precedes recessions
5. **Real GDP vs Median Income:** Economic growth vs household prosperity
6. **Core CPI vs Headline CPI:** Underlying inflation vs volatile components

## Work Progress Log

| Date | Action | Status |
|------|--------|--------|
| 2026-08-14 | Project setup, FRED data series research | Completed |
| 2026-08-14 | Architecture documentation | Completed |
| 2026-08-14 | Create fetch_data.py, pull all 14 series (13 indicators + USREC) | Completed |
| 2026-08-14 | Merge to monthly resolution, generate plots | Completed |
| 2026-08-14 | Initial Git commits, push to GitHub | Completed |
| 2026-08-15 | Plot refinements: forward-fill quarterly/annual, recession shading, start 1990 | Completed |
| 2026-08-16 | COVID period econometrics (covid_analysis.py): OLS models, correlation, lag analysis | Completed |
| 2026-08-18 | Forecasting (forecast.py): ARMA, ARIMA, VAR, VECM with 2019-2023 holdout | Completed |
| 2026-08-18 | README documentation with full results and plots | Completed |
| 2026-08-18 | Fix requirements (statsmodels, numpy), move API key to .env, doc sync | Completed |
