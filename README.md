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
