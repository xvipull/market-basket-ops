# Retail Assortment & Basket Economics Intelligence

Decision-support analytics for improving retail assortment productivity, basket economics, and store execution.

## Purpose

This project turns item- and transaction-level retail data into an auditable view of what customers buy together, where assortment performance differs, and which actions can improve sales, margin, availability, and basket value.

## Architecture

```text
POS / product / inventory / store master / promotion sources
                         |
                    data/raw
                         |
                data/staging  <--- SQL quality checks
                         |
              curated analytic model
                    /       \
                src       sql
                    \       /
          Power BI / Excel / reports
```

## Repository layout

- `docs/` — charter, KPI definitions, data dictionary, and assumptions.
- `data/raw/` — immutable source extracts; never commit production data.
- `data/staging/` — validated, standardized intermediate datasets.
- `sql/` and `src/` — transformation and analytic logic.
- `notebooks/` — exploratory analysis only; production logic graduates to `src/` or `sql/`.
- `powerbi/`, `excel/`, and `reports/` — governed business outputs.
- `tests/` — data-quality and calculation tests.

## Screenshots

| Assortment opportunity dashboard | Basket affinity explorer |
| --- | --- |
| _Placeholder: add Power BI screenshot_ | _Placeholder: add basket-analysis screenshot_ |

## Getting started

1. Review [requirements](docs/requirements.md), the [KPI catalog](docs/kpi_catalog.md), and the [data dictionary](docs/data_dictionary.md).
2. Place approved, de-identified extracts in `data/raw/` outside version control.
3. Run quality checks before publishing any report.

## Governance

Use only approved retail data. Do not add customer-identifiable, payment-card, employee, or supplier-confidential data to this repository.
