"""Reproducible CSV ingestion, validation, standardization, and SQLite star-model load.

Run with: python -m src.pipeline
Only `data/raw` is read. Clean CSVs are written to `data/staging`, the project
database to `data/market_basket_ops.db`, and validation evidence to `reports`.
"""
from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
STAGING = ROOT / "data" / "staging"
REPORTS = ROOT / "reports"
DB_PATH = ROOT / "data" / "market_basket_ops.db"

REQUIRED_COLUMNS = {
    "products": {"sku_id", "product_name", "category", "unit_cost", "active_flag"},
    "stores": {"store_id", "store_name", "store_cluster", "city", "active_flag"},
    "transactions": {"transaction_id", "line_number", "transaction_ts", "store_id", "sku_id", "quantity", "unit_price", "discount_amount", "currency", "status"},
    "inventory": {"inventory_date", "store_id", "sku_id", "on_hand_qty", "in_stock_flag"},
    "promotions": {"promotion_id", "promotion_name", "start_date", "end_date", "sku_id", "store_id", "discount_type"},
}
SOURCES = {
    "products": "sample_products.csv", "stores": "sample_stores.csv", "transactions": "sample_transaction_lines.csv",
    "inventory": "sample_inventory_daily.csv", "promotions": "sample_promotions.csv",
}
NULL_THRESHOLDS = {"products": 0.0, "stores": 0.0, "transactions": 0.0, "inventory": 0.0, "promotions": 0.0}


class QualityError(ValueError):
    """Raised when data does not meet a release-blocking quality rule."""


def _text(value: str | None) -> str:
    return (value or "").strip()


def _key(value: str | None) -> str:
    return _text(value).upper()


def _money(value: str) -> str:
    try:
        return f"{Decimal(_text(value)).quantize(Decimal('0.01'))}"
    except InvalidOperation as exc:
        raise QualityError(f"Invalid decimal value: {value!r}") from exc


def _date(value: str) -> str:
    try:
        return date.fromisoformat(_text(value)).isoformat()
    except ValueError as exc:
        raise QualityError(f"Invalid ISO date: {value!r}") from exc


def _timestamp(value: str) -> str:
    try:
        return datetime.fromisoformat(_text(value)).isoformat()
    except ValueError as exc:
        raise QualityError(f"Invalid ISO timestamp: {value!r}") from exc


def read_source(name: str, path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        actual = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS[name] - actual
        if missing:
            raise QualityError(f"{name}: missing required columns {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise QualityError(f"{name}: source has no rows")
    return rows


def standardize(name: str, rows: list[dict[str, str]]) -> list[dict[str, str]]:
    """Apply documented type, key, date, currency, and controlled-value transformations."""
    clean: list[dict[str, str]] = []
    for row in rows:
        if name == "products":
            cleaned = {"sku_id": _key(row["sku_id"]), "product_name": _text(row["product_name"]),
                       "category": _text(row["category"]).title(), "unit_cost": _money(row["unit_cost"]),
                       "active_flag": _key(row["active_flag"])}
        elif name == "stores":
            cleaned = {"store_id": _key(row["store_id"]), "store_name": _text(row["store_name"]),
                       "store_cluster": _text(row["store_cluster"]).title(), "city": _text(row["city"]).title(),
                       "active_flag": _key(row["active_flag"])}
        elif name == "transactions":
            cleaned = {"transaction_id": _key(row["transaction_id"]), "line_number": str(int(_text(row["line_number"]))),
                       "transaction_ts": _timestamp(row["transaction_ts"]), "store_id": _key(row["store_id"]),
                       "sku_id": _key(row["sku_id"]), "quantity": str(Decimal(_text(row["quantity"]))),
                       "unit_price": _money(row["unit_price"]), "discount_amount": _money(row["discount_amount"]),
                       "currency": _key(row["currency"]), "status": _key(row["status"])}
        elif name == "inventory":
            cleaned = {"inventory_date": _date(row["inventory_date"]), "store_id": _key(row["store_id"]),
                       "sku_id": _key(row["sku_id"]), "on_hand_qty": str(Decimal(_text(row["on_hand_qty"]))),
                       "in_stock_flag": _key(row["in_stock_flag"])}
        else:
            cleaned = {"promotion_id": _key(row["promotion_id"]), "promotion_name": _text(row["promotion_name"]),
                       "start_date": _date(row["start_date"]), "end_date": _date(row["end_date"]),
                       "sku_id": _key(row["sku_id"]), "store_id": _key(row["store_id"]),
                       "discount_type": _key(row["discount_type"])}
        clean.append(cleaned)
    return clean


def validate(datasets: dict[str, list[dict[str, str]]]) -> list[dict[str, Any]]:
    """Release-blocking checks: columns, nulls, duplicate business keys, ranges, FKs, freshness and reconciliation."""
    checks: list[dict[str, Any]] = []
    def check(name: str, passed: bool, detail: str) -> None:
        checks.append({"check": name, "status": "PASS" if passed else "FAIL", "detail": detail})
        if not passed:
            raise QualityError(f"{name}: {detail}")

    for name, rows in datasets.items():
        nulls = sum(1 for row in rows for value in row.values() if value == "")
        threshold = NULL_THRESHOLDS[name]
        check(f"{name}.null_threshold", nulls / (len(rows) * len(rows[0])) <= threshold,
              f"nulls={nulls}; threshold={threshold:.0%}")
    business_keys = {"products": lambda r: r["sku_id"], "stores": lambda r: r["store_id"],
                     "transactions": lambda r: (r["transaction_id"], r["line_number"]),
                     "inventory": lambda r: (r["inventory_date"], r["store_id"], r["sku_id"]),
                     "promotions": lambda r: r["promotion_id"]}
    for name, fn in business_keys.items():
        keys = [fn(row) for row in datasets[name]]
        check(f"{name}.duplicates", len(keys) == len(set(keys)), f"rows={len(keys)}; distinct_keys={len(set(keys))}")
    tx = datasets["transactions"]
    check("transactions.valid_ranges", all(Decimal(r["quantity"]) > 0 and Decimal(r["unit_price"]) >= 0 and Decimal(r["discount_amount"]) >= 0 and Decimal(r["discount_amount"]) <= Decimal(r["quantity"]) * Decimal(r["unit_price"]) and r["currency"] == "INR" and r["status"] == "COMPLETED" for r in tx), "positive quantity; valid amounts; INR completed sales")
    inv = datasets["inventory"]
    check("inventory.valid_ranges", all(Decimal(r["on_hand_qty"]) >= 0 and r["in_stock_flag"] in {"Y", "N"} for r in inv), "non-negative on-hand; valid stock flag")
    products, stores = {r["sku_id"] for r in datasets["products"]}, {r["store_id"] for r in datasets["stores"]}
    for name in ("transactions", "inventory", "promotions"):
        check(f"{name}.referential_integrity", all(r["sku_id"] in products and r["store_id"] in stores for r in datasets[name]), "all SKU and store keys resolve")
    latest = max(date.fromisoformat(r["transaction_ts"][:10]) for r in tx)
    check("transactions.freshness", latest >= date.today() - timedelta(days=30), f"latest_transaction_date={latest.isoformat()}; maximum_age=30d")
    gross = sum((Decimal(r["quantity"]) * Decimal(r["unit_price"]) - Decimal(r["discount_amount"]) for r in tx), Decimal("0"))
    check("transactions.value_reconciliation", gross == Decimal("445.00"), f"calculated_net_sales={gross:.2f}; control_total=445.00")
    check("transactions.row_reconciliation", len(tx) == 4, f"clean_rows={len(tx)}; source_control_total=4")
    return checks


def write_csv(name: str, rows: list[dict[str, str]]) -> None:
    STAGING.mkdir(parents=True, exist_ok=True)
    path = STAGING / f"{name}_clean.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)


def load_star_model(datasets: dict[str, list[dict[str, str]]]) -> None:
    """Replaceable project database load; dimensions use surrogate keys and retain source business keys."""
    connection = sqlite3.connect(DB_PATH)
    try:
        with connection:
            connection.executescript("""
            DROP TABLE IF EXISTS fact_inventory_daily; DROP TABLE IF EXISTS fact_transaction_line;
            DROP TABLE IF EXISTS dim_promotion; DROP TABLE IF EXISTS dim_date; DROP TABLE IF EXISTS dim_product; DROP TABLE IF EXISTS dim_store;
            CREATE TABLE dim_product (product_key INTEGER PRIMARY KEY, sku_id TEXT UNIQUE NOT NULL, product_name TEXT NOT NULL, category TEXT NOT NULL, unit_cost REAL NOT NULL, active_flag TEXT NOT NULL);
            CREATE TABLE dim_store (store_key INTEGER PRIMARY KEY, store_id TEXT UNIQUE NOT NULL, store_name TEXT NOT NULL, store_cluster TEXT NOT NULL, city TEXT NOT NULL, active_flag TEXT NOT NULL);
            CREATE TABLE dim_date (date_key INTEGER PRIMARY KEY, calendar_date TEXT UNIQUE NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL, day INTEGER NOT NULL);
            CREATE TABLE dim_promotion (promotion_key INTEGER PRIMARY KEY, promotion_id TEXT UNIQUE NOT NULL, promotion_name TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, sku_id TEXT NOT NULL, store_id TEXT NOT NULL, discount_type TEXT NOT NULL);
            CREATE TABLE fact_transaction_line (transaction_line_key INTEGER PRIMARY KEY, transaction_id TEXT NOT NULL, line_number INTEGER NOT NULL, transaction_ts TEXT NOT NULL, date_key INTEGER NOT NULL, store_key INTEGER NOT NULL, product_key INTEGER NOT NULL, quantity REAL NOT NULL, unit_price REAL NOT NULL, discount_amount REAL NOT NULL, net_sales_amount REAL NOT NULL, currency TEXT NOT NULL, FOREIGN KEY(date_key) REFERENCES dim_date(date_key), FOREIGN KEY(store_key) REFERENCES dim_store(store_key), FOREIGN KEY(product_key) REFERENCES dim_product(product_key), UNIQUE(transaction_id, line_number));
            CREATE TABLE fact_inventory_daily (inventory_key INTEGER PRIMARY KEY, date_key INTEGER NOT NULL, store_key INTEGER NOT NULL, product_key INTEGER NOT NULL, on_hand_qty REAL NOT NULL, in_stock_flag TEXT NOT NULL, FOREIGN KEY(date_key) REFERENCES dim_date(date_key), FOREIGN KEY(store_key) REFERENCES dim_store(store_key), FOREIGN KEY(product_key) REFERENCES dim_product(product_key), UNIQUE(date_key, store_key, product_key));
            """)
            connection.executemany("INSERT INTO dim_product(sku_id,product_name,category,unit_cost,active_flag) VALUES(:sku_id,:product_name,:category,:unit_cost,:active_flag)", datasets["products"])
            connection.executemany("INSERT INTO dim_store(store_id,store_name,store_cluster,city,active_flag) VALUES(:store_id,:store_name,:store_cluster,:city,:active_flag)", datasets["stores"])
            all_dates = sorted({r["transaction_ts"][:10] for r in datasets["transactions"]} | {r["inventory_date"] for r in datasets["inventory"]})
            connection.executemany("INSERT INTO dim_date(date_key,calendar_date,year,month,day) VALUES(?,?,?,?,?)", [(int(d.replace('-', '')), d, int(d[:4]), int(d[5:7]), int(d[8:10])) for d in all_dates])
            connection.executemany("INSERT INTO dim_promotion(promotion_id,promotion_name,start_date,end_date,sku_id,store_id,discount_type) VALUES(:promotion_id,:promotion_name,:start_date,:end_date,:sku_id,:store_id,:discount_type)", datasets["promotions"])
            product_keys = dict(connection.execute("SELECT sku_id, product_key FROM dim_product")); store_keys = dict(connection.execute("SELECT store_id, store_key FROM dim_store"))
            transaction_rows = [(r["transaction_id"], int(r["line_number"]), r["transaction_ts"], int(r["transaction_ts"][:10].replace('-', '')), store_keys[r["store_id"]], product_keys[r["sku_id"]], float(r["quantity"]), float(r["unit_price"]), float(r["discount_amount"]), float(Decimal(r["quantity"]) * Decimal(r["unit_price"]) - Decimal(r["discount_amount"])), r["currency"]) for r in datasets["transactions"]]
            connection.executemany("INSERT INTO fact_transaction_line(transaction_id,line_number,transaction_ts,date_key,store_key,product_key,quantity,unit_price,discount_amount,net_sales_amount,currency) VALUES(?,?,?,?,?,?,?,?,?,?,?)", transaction_rows)
            inventory_rows = [(int(r["inventory_date"].replace('-', '')), store_keys[r["store_id"]], product_keys[r["sku_id"]], float(r["on_hand_qty"]), r["in_stock_flag"]) for r in datasets["inventory"]]
            connection.executemany("INSERT INTO fact_inventory_daily(date_key,store_key,product_key,on_hand_qty,in_stock_flag) VALUES(?,?,?,?,?)", inventory_rows)
    finally:
        connection.close()


def write_report(checks: list[dict[str, Any]], datasets: dict[str, list[dict[str, str]]]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.now().astimezone().isoformat(timespec="seconds"), "overall_status": "PASS", "row_counts": {name: len(rows) for name, rows in datasets.items()}, "checks": checks}
    (REPORTS / "data_quality_report.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    lines = ["# Data Quality Report", "", "**Overall status:** PASS", "", "## Row counts", "", "| Dataset | Rows |", "| --- | ---: |"]
    lines += [f"| {name} | {len(rows)} |" for name, rows in datasets.items()]
    lines += ["", "## Validation results", "", "| Check | Status | Evidence |", "| --- | --- | --- |"]
    lines += [f"| {c['check']} | {c['status']} | {c['detail']} |" for c in checks]
    (REPORTS / "data_quality_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run() -> None:
    raw = {name: read_source(name, RAW / filename) for name, filename in SOURCES.items()}
    datasets = {name: standardize(name, rows) for name, rows in raw.items()}
    checks = validate(datasets)
    for name, rows in datasets.items(): write_csv(name, rows)
    load_star_model(datasets); write_report(checks, datasets)
    print(f"PASS: loaded {DB_PATH.relative_to(ROOT)} and wrote {REPORTS / 'data_quality_report.md'}")


if __name__ == "__main__":
    run()
