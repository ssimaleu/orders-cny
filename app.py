#!/usr/bin/env python3
"""Flask frontend for the orders SQLite database.

- Connects to orders.db (SQLite backend)
- Main page shows the merged orders table and the region summary table
- Reads the database on every request and the page polls /api/tables
  every 5 seconds, so it updates automatically when the database changes.

Run:  python3 app.py   ->  http://127.0.0.1:5000
"""
import sqlite3
from pathlib import Path

from flask import Flask, jsonify, render_template

DB_PATH = Path(__file__).resolve().parent / "orders.db"

app = Flask(__name__)


def query_db(sql: str) -> list[dict]:
    """Query the SQLite database and return rows as dicts (fresh connection each time)."""
    if not DB_PATH.exists():
        return []
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        return [dict(row) for row in con.execute(sql).fetchall()]
    finally:
        con.close()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/tables")
def api_tables():
    """Both tables as JSON — called by the page every 5 s for auto-update."""
    return jsonify(
        orders=query_db("SELECT * FROM orders ORDER BY order_id"),
        summary=query_db("SELECT * FROM region_summary ORDER BY avg_amount_cny DESC"),
    )


if __name__ == "__main__":
    app.run(debug=True)
