# Sprint 1 Retrospective

## Completed
- Environment and project structure created.
- 12 Excel sources normalized and loaded.
- 16 DQ rules implemented.
- SQLite schema with foreign keys enabled.
- Load audit and validation outputs generated.
- 35+ ETL/normalization tests supplied.
- 10 exploratory SQL queries supplied.

## Data-quality actions
Critical orphan child records are rejected before insertion so `PRAGMA foreign_key_check` remains empty. Duplicate annual `(company_id, year)` records in the core annual statements are de-duplicated using the last occurrence rule.

## Follow-up
Warning-level DQ findings remain analyst-review items and should be addressed or accepted during subsequent ratio-engine work.
