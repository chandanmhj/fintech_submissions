# Sprint 6 validation (reference database)

- Clustering executed against the included Sprint 5 reference database and processed 92 company records.
- Generated cluster labels, elbow curve, cluster profiles, correlation heatmap, outlier report, and portfolio statistics.
- Automated smoke tests: 5 passed.
- API smoke checks returned HTTP 200 for health, companies list (92 rows), TCS ratios, sectors, portfolio statistics, and OpenAPI.
- The reference DB exposes 10 distinct broad sectors, not 11. Do not report 11 sector groups without reconciling the source data.
- Acceptance gates requiring local dashboard tests, manual spot-checks, 60+ total tests, load tests, PDF visual inspection, and team-lead signature remain pending.
