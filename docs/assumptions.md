# Assumptions, Risks, and Controls

| ID | Assumption or risk | Impact | Control / mitigation | Owner |
| --- | --- | --- | --- | --- |
| A1 | POS transaction IDs reliably group lines into a basket. | Invalid basket affinity if false. | Reconcile line counts and sample receipts each release. | Retail Data Engineering |
| A2 | Product hierarchy is effective-dated and supplied daily. | Misclassified category performance. | Persist hierarchy version and publish unmapped SKU exceptions. | Merchandising Master Data |
| A3 | Inventory is an availability proxy, not a direct observation of shelf stock. | False stockout conclusions. | Label metric clearly; validate against cycle counts and store feedback. | Supply Chain Data Product |
| R1 | Promotions, holidays, and price changes confound affinities and productivity. | Incorrect action prioritization. | Include promotion/calendar flags and comparator periods. | Category Analytics |
| R2 | Sparse baskets create unstable lift metrics. | Spurious pair recommendations. | Apply minimum basket-count thresholds and confidence labels. | Category Analytics |
| R3 | Store cluster definitions become stale. | Poor localization decisions. | Quarterly review; effective-date cluster assignments. | Store Operations Analytics |
| R4 | Users interpret observed change as causal. | Unsubstantiated business claims. | Require a documented test/comparator for intervention uplift. | Product Owner |
| R5 | Sensitive data enters extracts or repository. | Privacy and compliance breach. | Automated scanning, least-privilege access, no raw production data in Git. | Information Security |

## Decision principles

- Protect customer choice: do not remove items solely because direct sales are low without evaluating attachment, margin, availability, and substitution.
- Prefer category- and cluster-relative comparisons over chain-wide rankings alone.
- Treat analytics as a recommendation for human review, not an automated execution instruction.
