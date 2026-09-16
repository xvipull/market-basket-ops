# Data Quality Report

**Overall status:** PASS

## Row counts

| Dataset | Rows |
| --- | ---: |
| products | 4 |
| stores | 2 |
| transactions | 4 |
| inventory | 4 |
| promotions | 1 |

## Validation results

| Check | Status | Evidence |
| --- | --- | --- |
| products.null_threshold | PASS | nulls=0; threshold=0% |
| stores.null_threshold | PASS | nulls=0; threshold=0% |
| transactions.null_threshold | PASS | nulls=0; threshold=0% |
| inventory.null_threshold | PASS | nulls=0; threshold=0% |
| promotions.null_threshold | PASS | nulls=0; threshold=0% |
| products.duplicates | PASS | rows=4; distinct_keys=4 |
| stores.duplicates | PASS | rows=2; distinct_keys=2 |
| transactions.duplicates | PASS | rows=4; distinct_keys=4 |
| inventory.duplicates | PASS | rows=4; distinct_keys=4 |
| promotions.duplicates | PASS | rows=1; distinct_keys=1 |
| transactions.valid_ranges | PASS | positive quantity; valid amounts; INR completed sales |
| inventory.valid_ranges | PASS | non-negative on-hand; valid stock flag |
| transactions.referential_integrity | PASS | all SKU and store keys resolve |
| inventory.referential_integrity | PASS | all SKU and store keys resolve |
| promotions.referential_integrity | PASS | all SKU and store keys resolve |
| transactions.freshness | PASS | latest_transaction_date=2026-09-15; maximum_age=30d |
| transactions.value_reconciliation | PASS | calculated_net_sales=445.00; control_total=445.00 |
| transactions.row_reconciliation | PASS | clean_rows=4; source_control_total=4 |
