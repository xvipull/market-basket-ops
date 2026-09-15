# KPI Catalog

All currency values use the reporting currency; reporting periods follow the retail calendar. Metrics must show filters, date range, hierarchy version, and refresh timestamp.

| KPI | Definition | Formula | Grain / guardrail | Owner |
| --- | --- | --- | --- | --- |
| Net sales | Sales after returns and approved discounts | `sum(net_sales_amount)` | SKU × store × day; exclude voided transactions | Finance / POS |
| Gross margin | Profit after cost of goods sold | `net_sales - cogs` | Use approved landed-cost version | Finance |
| Gross margin % | Margin proportion of net sales | `gross_margin / net_sales` | Null when net sales is zero | Finance |
| Basket value | Average net sales per completed basket | `net_sales / distinct(transaction_id)` | Exclude returns-only and voided baskets | Category Analytics |
| Units per basket | Average units purchased per basket | `sum(quantity) / distinct(transaction_id)` | Same basket inclusion as basket value | Category Analytics |
| Attachment rate | Share of anchor-item baskets that also contain target | `baskets(anchor AND target) / baskets(anchor)` | Directional; show anchor and target | Category Analytics |
| Pair support | Share of all baskets containing both items | `baskets(anchor AND target) / all_baskets` | Report only above agreed minimum count | Category Analytics |
| Lift | Pair association relative to independent purchase | `support(A,B) / (support(A) * support(B))` | Descriptive, not causal; suppress sparse pairs | Category Analytics |
| Sales per facing proxy | Sales normalized by approved facing count when available | `net_sales / facings` | Do not calculate without current planogram data | Merchandising |
| Availability proxy | In-stock share of eligible SKU-store-day observations | `in_stock_days / eligible_days` | Clearly label source and stockout rules | Store Operations |
| Assortment productivity | Profit contribution per listed SKU or per space proxy | `gross_margin / active_listed_skus` | Compare within category and store cluster | Merchandising |
| Intervention uplift | Change after action versus approved baseline/comparator | documented test formula | Requires action date and comparison design | Product Owner |
