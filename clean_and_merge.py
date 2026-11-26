#!/usr/bin/env python3
"""clean_and_merge.py

ETL pipeline:
1. Read the two data files (data/orders.csv, data/customers.csv)
2. Remove duplicate rows
3. Convert all amounts to CNY into a new column 'amount_cny'
   (rates: USD=6.9, EUR=7.5, CNY=1.0, JPY=0.05)
4. Merge orders with customers on 'customer_id'
5. Write the merged data to an SQLite database (orders.db)
6. Create a summary table: average 'amount_cny' by region
"""
import sqlite3
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "orders.db"

# Conversion rates to CNY
RATES = {"USD": 6.9, "EUR": 7.5, "CNY": 1.0, "JPY": 0.05}


def load_and_clean() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read the two data files, clean duplicates and convert amounts to CNY."""
    orders = pd.read_csv(DATA_DIR / "orders.csv")
    customers = pd.read_csv(DATA_DIR / "customers.csv")

    before = len(orders)
    orders = orders.drop_duplicates().reset_index(drop=True)
    print(f"Duplicates removed: {before - len(orders)}")

    orders["amount_cny"] = (
        orders["amount"] * orders["currency"].str.strip().map(RATES)
    ).round(2)

    unknown = orders.loc[orders["amount_cny"].isna(), "currency"].unique()
    if len(unknown):
        raise ValueError(f"Unknown currency(ies): {list(unknown)}")
    return orders, customers


def main() -> None:
    orders, customers = load_and_clean()

    # Merge order data and customer data on 'customer_id'
    merged = orders.merge(customers, on="customer_id", how="left")

    # Summary table: average amount_cny by region
    summary = (
        merged.groupby("region", as_index=False)["amount_cny"]
        .mean()
        .round(2)
        .rename(columns={"amount_cny": "avg_amount_cny"})
    )

    # Write to SQLite
    with sqlite3.connect(DB_PATH) as con:
        merged.to_sql("orders", con, if_exists="replace", index=False)
        summary.to_sql("region_summary", con, if_exists="replace", index=False)

    print(f"Merged {len(merged)} orders -> {DB_PATH.name} (table 'orders')")
    print("Average amount_cny by region:")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
