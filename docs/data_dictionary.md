# Data Dictionary

The canonical model uses a transaction-line fact table plus conformed product, store, calendar, promotion, and inventory dimensions. Identifiers are technical keys and must not contain direct customer or payment information.

| Dataset | Field | Type | Description | Data quality rule |
| --- | --- | --- | --- | --- |
| `fact_transaction_line` | `transaction_id` | string | Unique completed basket identifier | Required; unique with line number |
| `fact_transaction_line` | `transaction_ts` | timestamp | Local transaction time | Required; valid retail-calendar mapping |
| `fact_transaction_line` | `store_id` | string | Selling location key | Required; joins to active store |
| `fact_transaction_line` | `sku_id` | string | Sold SKU key | Required; joins to active product/hierarchy |
| `fact_transaction_line` | `quantity` | decimal | Net units sold, including returns when approved | Non-zero; return convention documented |
| `fact_transaction_line` | `net_sales_amount` | decimal(18,2) | Sales after discount and returns | Reconciles to POS controls |
| `fact_transaction_line` | `cogs_amount` | decimal(18,2) | Approved cost of goods sold | Flag missing cost rather than impute silently |
| `dim_product` | `sku_id` | string | Product business key | Unique active record per effective date |
| `dim_product` | `category_id` | string | Category hierarchy key | Required for pilot SKUs |
| `dim_product` | `assortment_status` | string | Listed, delisted, seasonal, or test | Controlled vocabulary |
| `dim_store` | `store_id` | string | Store business key | Unique active record per effective date |
| `dim_store` | `store_cluster` | string | Comparable store grouping | Owned by Store Operations Analytics |
| `fact_inventory_daily` | `on_hand_qty` | decimal | End-of-day on-hand quantity | Non-negative unless source correction flag |
| `fact_inventory_daily` | `in_stock_flag` | boolean | Approved availability indicator | Rule version recorded |
| `dim_promotion` | `promotion_id` | string | Promotion event key | Valid dates and product/store scope required |

## Derived fields

- `basket_id`: `transaction_id` after excluding voided and non-merchandise lines under the agreed rule.
- `gross_margin_amount`: `net_sales_amount - cogs_amount`.
- `is_affinity_eligible`: true only for valid completed baskets meeting minimum analytic rules.
- `hierarchy_version`: product hierarchy effective on the transaction date.
