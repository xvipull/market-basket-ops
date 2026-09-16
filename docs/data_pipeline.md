# Data Pipeline and Quality Controls

## Chosen dataset

The repository includes a small, synthetic Indian grocery-retail extract in `data/raw/sample_*.csv`. It mirrors the approved source contracts (POS lines, product, store, inventory, and promotion data) without production or personal data. Production extracts must be deposited in governed storage and conform to these contracts.

## Reproducible run

```bash
python3 -m src.pipeline
python3 -m unittest discover -s tests -v
```

The pipeline never modifies raw inputs. It writes standardized CSVs to `data/staging/`, a replaceable SQLite project database to `data/market_basket_ops.db`, and a JSON/Markdown quality report to `reports/`.

## Transformation contract

| Input | Transformation | Output/control |
| --- | --- | --- |
| Text fields | Trim whitespace | Empty values fail configured null thresholds |
| Business keys | Uppercase `sku_id`, `store_id`, `transaction_id`, `promotion_id` | Consistent joins; raw values remain unchanged |
| Categories/cities/clusters | Title-case presentation labels | Standardized reporting values |
| Dates/timestamps | Parse ISO-8601 and serialize ISO | Invalid values fail load |
| Currency/status/flags | Uppercase controlled values | Transactions must be completed INR records; flags must be Y/N |
| Money | Parse with `Decimal`, round to two decimals | Net sales = quantity × unit price − discount |

## Quality gates

The load fails before writing the model if a required column is missing, a source is empty, null thresholds are exceeded, business keys duplicate, quantities/prices/discounts/inventory are invalid, dimension references do not resolve, POS data is older than 30 days, or configured transaction row/value controls fail. Evidence is published in `reports/data_quality_report.*` only after all gates pass.

## Dimensional model

`fact_transaction_line` has one row per completed transaction line; its natural business key is `(transaction_id, line_number)`. `fact_inventory_daily` has one row per `(calendar date, store, SKU)`. Both facts use `date_key`, `store_key`, and `product_key` surrogate keys. Dimensions retain `sku_id`, `store_id`, and `promotion_id` business keys for traceability. `dim_promotion` is currently a conformed reference dimension; promotion attribution is intentionally deferred until a governed allocation rule is approved.
