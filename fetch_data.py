"""
Fetch economic data from FRED (Federal Reserve Economic Data) API.
Source: https://fred.stlouisfed.org/
"""

import os
import requests
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FRED_API_KEY = os.getenv("FRED_API_KEY")
if not FRED_API_KEY:
    raise SystemExit(
        "FRED_API_KEY is not set. Create a .env file next to this script "
        "(get a free key at https://fred.stlouisfed.org/docs/api/api_key/)."
    )
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Series configurations: (series_id, output_filename, units, frequency)
SERIES_CONFIG = [
    # Inflation
    ("CPIAUCSL", "cpi_urban_consumers.csv", "lin", "m"),
    ("CPILFESL", "cpi_core.csv", "lin", "m"),
    # Housing
    ("MSPUS", "median_house_price.csv", "lin", "q"),
    ("CSUSHPINSA", "case_shiller_hpi.csv", "lin", "m"),
    ("MORTGAGE30US", "mortgage_rate_30yr.csv", "lin", "w"),
    # Taxes
    ("FYFR", "federal_receipts.csv", "lin", "a"),
    # Monetary Policy
    ("FEDFUNDS", "federal_funds_rate.csv", "lin", "m"),
    ("T10Y2Y", "treasury_spread_10y2y.csv", "lin", "d"),
    # GDP
    ("GDP", "gdp.csv", "lin", "q"),
    ("GDPC1", "real_gdp.csv", "lin", "q"),
    # Employment
    ("UNRATE", "unemployment_rate.csv", "lin", "m"),
    ("CIVPART", "labor_participation.csv", "lin", "m"),
    # Income
    ("MEHOINUSA646N", "median_household_income.csv", "lin", "a"),
    # Recession indicator
    ("USREC", "usrec.csv", "lin", "m"),
]


def fetch_series(series_id: str, api_key: str, file_type: str = "json") -> list[dict]:
    """Fetch observations for a single FRED series."""
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": file_type,
        "sort_order": "asc",
    }
    resp = requests.get(FRED_BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return data.get("observations", [])


def observations_to_dataframe(observations: list[dict]) -> pd.DataFrame:
    """Convert FRED observations to a DataFrame."""
    records = []
    for obs in observations:
        date = obs.get("date", "")
        value = obs.get("value", ".")
        # FRED uses "." for missing values
        if value == ".":
            value = None
        else:
            value = float(value)
        records.append({"date": date, "value": value})
    return pd.DataFrame(records)


def main():
    data_dir = Path(__file__).parent / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"FRED API Key: {FRED_API_KEY[:8]}...")
    print(f"Fetching {len(SERIES_CONFIG)} series from FRED...\n")

    for series_id, filename, _units, _freq in SERIES_CONFIG:
        try:
            print(f"  Fetching {series_id} -> {filename} ... ", end="")
            observations = fetch_series(series_id, FRED_API_KEY)
            df = observations_to_dataframe(observations)
            filepath = data_dir / filename
            df.to_csv(filepath, index=False)
            print(f"OK ({len(df)} rows)")
        except requests.exceptions.HTTPError as e:
            print(f"ERROR: {e}")
        except Exception as e:
            print(f"ERROR: {e}")

    print(f"\nDone. CSVs saved to: {data_dir}")


if __name__ == "__main__":
    main()
