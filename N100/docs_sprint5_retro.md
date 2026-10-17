# Sprint 5 Retrospective

## What went well
- Financial NLP rules are deterministic and traceable by rule ID.
- Cash-flow classification and report generation are reproducible from the SQLite database.
- Report tables use wrapped Paragraph cells to reduce overflow risk.

## Challenges / caveats
- Source analysis text includes TTM / 1 Year / Last Year variants that intentionally fail the requested N Years regex and require manual review.
- Cash flow source data uses investing activity as a CapEx proxy.
- Supplied snapshot has 10 broad sectors, so a consolidated All Sectors PDF is used as the 11th report.

## Follow-ups
- Visually review five representative tearsheets and all sector PDF page breaks.
- Confirm local database has all original financial years before final sign-off.
- Review all `parse_failures.csv` and `cagr_cross_validation.csv` rows.
