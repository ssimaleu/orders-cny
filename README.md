# Orders → CNY Data Pipeline & Dashboard

ETL exercise: clean, convert, merge order/customer data into SQLite and
visualize it with a Flask frontend, all automated with GitHub Actions.

## Project structure

```
data/orders.csv          raw order data (with duplicates, mixed currencies)
data/customers.csv       customer data (id, name, region)
clean_and_merge.py       ETL script -> orders.db (SQLite)
app.py                   Flask frontend
templates/index.html     dashboard page (auto-refresh 5 s)
.github/workflows/update-data.yml   CI: rebuild DB when data/ changes
```

## 1. Run the ETL script

```bash
pip install -r requirements.txt
python clean_and_merge.py
```

What it does:
1. Reads `data/orders.csv` and `data/customers.csv`
2. Removes duplicate rows
3. Converts amounts to CNY (USD=6.9, EUR=7.5, CNY=1.0, JPY=0.05) → new column `amount_cny`
4. Merges orders ⋈ customers on `customer_id`
5. Writes the merged table `orders` to `orders.db` (SQLite)
6. Creates `region_summary`: average `amount_cny` per region

## 2. Run the Flask app

```bash
python app.py        # http://127.0.0.1:5000
```

The main page shows the merged orders table and the per-region summary.
It connects to SQLite on every request and polls `/api/tables` every 5 s,
so it updates automatically when the database changes.

## 3. GitHub Actions

`update-data.yml` triggers when any file under `data/` is pushed. It
installs Python 3.11 + pandas/flask, runs `clean_and_merge.py` to update
the database, and commits the refreshed `orders.db` back to the repo.
