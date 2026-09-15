# Project Charter — Retail Assortment & Basket Economics Intelligence

## Charter

**Sponsor:** VP, Merchandising Analytics  
**Product owner:** Director, Category Strategy  
**Objective:** Deliver a trusted analytics product that identifies assortment, adjacency, promotion, and store-execution opportunities using transaction, product, inventory, and store data. The product will help teams grow profitable baskets while protecting availability and customer choice.

## Stakeholder personas

| Persona | Primary goals | Decisions enabled | Typical cadence |
| --- | --- | --- | --- |
| Merchandising leader | Grow category margin and productive assortment | Approve category resets, assortment guardrails, vendor conversations | Monthly / quarterly |
| Category manager | Improve item mix, attachment, and promotional economics | Add, retain, replace, or rationalize SKUs; plan adjacencies and promotions | Weekly / seasonal |
| Store operations leader | Make assortment executable in stores | Prioritize replenishment, shelf compliance, localized assortment, and labor actions | Daily / weekly |

## Business problem

Teams currently reconcile sales, inventory, promotions, and customer-basket signals across disconnected reports. This obscures which items drive profitable trips, which apparent low sellers are attachment or traffic drivers, and where store-level availability is suppressing demand. Decisions are slower, inconsistent, and difficult to measure.

## Decisions this product must support

1. Which SKUs should be expanded, retained, replaced, or reviewed by category and store cluster?
2. Which product pairs or missions merit cross-merchandising, adjacency, bundled promotion, or digital recommendation?
3. Where are stockouts, assortment gaps, or execution failures reducing sales and margin?
4. Which store clusters require localized assortment versus enterprise-standard ranges?
5. Did an assortment, promotion, or execution intervention improve incremental sales, gross margin, availability, and basket value?

## Scope

**In scope**

- SKU, category, store, transaction, inventory, promotion, and calendar data.
- Basket affinity, attachment rate, item/category productivity, availability proxy, and store-cluster comparisons.
- Governed Power BI and Excel outputs, refresh monitoring, data-quality checks, and decision logs.
- Pilot categories and stores agreed by Merchandising and Store Operations.

**Out of scope**

- Automated ordering, pricing, or assortment changes in production systems.
- Customer-level targeting, loyalty activation, or personally identifiable customer profiling.
- Supplier scorecards, financial close reporting, and causal claims without an approved test design.
- Real-time point-of-sale decisioning in the initial release.

## Data owners and cadence

| Domain | Accountable owner | Minimum refresh | Use |
| --- | --- | --- | --- |
| POS transactions | Retail Data Engineering | Daily by 08:00 local time | Baskets, sales, units, margin |
| Product / hierarchy | Merchandising Master Data | Daily; intraday for approved changes | Assortment and category rollups |
| Inventory / availability | Supply Chain Data Product | Daily by 09:00 local time | Availability proxies and execution |
| Store master / cluster | Store Operations Analytics | Weekly or on change | Local comparisons |
| Promotion calendar | Commercial Planning | Daily | Promotion normalization |

## Security and privacy

Only aggregated or pseudonymized transaction records are permitted. Customer identifiers, payment data, names, addresses, employee identifiers, and free-text notes are excluded. Access follows least privilege through approved enterprise identity groups; data at rest and in transit must use company-approved encryption. Source extracts stay in governed storage; this repository contains code, metadata, and synthetic examples only. Retention and deletion follow the corporate records schedule.

## Assumptions and risks

See [assumptions](assumptions.md). Key risks include incomplete transaction linkage, misleading affinity due to promotions or stockouts, hierarchy changes, and users treating descriptive results as causal proof. Mitigations include reconciliation, freshness tests, promotion flags, availability context, versioned hierarchies, and controlled pilots.

## Acceptance criteria

1. Daily model refresh completes by 10:00 local time on at least 95% of scheduled business days, with visible freshness status.
2. Transaction sales and units reconcile to the approved POS control total within ±0.5% at enterprise and pilot-category level.
3. At least 99% of pilot SKU-store-day records resolve to an active product and store hierarchy; exceptions are published.
4. Each pilot category has a ranked assortment opportunity view, basket-pair view, availability context, and downloadable decision log.
5. Merchandising, Category Management, and Store Operations each complete a scenario review and rate decision usefulness at least 4/5 on average.
6. At least three approved pilot actions have baseline, measurement window, owner, and outcome recorded; no incremental claim is made without a comparison design.
