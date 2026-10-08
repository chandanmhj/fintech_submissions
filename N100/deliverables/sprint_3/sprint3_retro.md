# Sprint 3 Retrospective — Screener + Peer Engine

## Completed
- Configurable screener engine with 15 filterable metrics.
- Six analyst-editable presets.
- Sector-relative 0–100 composite quality score using P10/P90 winsorisation.
- Financials-sector D/E carve-out and Debt Free ICR handling.
- Peer percentile rankings for 11 peer groups and 10 metrics.
- Inverse D/E percentile ranking.
- Screener Excel report with one sheet per preset.
- Peer comparison Excel report with 11 peer-group sheets and median rows.
- Radar charts with peer-average overlays and standalone charts for companies without peer assignments.
- 14 Sprint 3 unit tests.

## Data Decisions
The supplied valuation snapshot (`market_cap.xlsx`) is available for 2024-03 only. Sprint 3 therefore uses 2024-03 as the common screening/peer year instead of mixing valuation data across fiscal years.

The source peer-group file contains 11 groups and 56 assigned companies; the remaining Nifty 100 companies have no peer-group assignment. Those companies are handled without raising errors and receive standalone radar charts.

Some fixed presets are narrower than five companies in the supplied source data. To satisfy the sprint's required review-set size without silently changing analyst thresholds, the engine preserves strict matches and adds clearly labelled `strict_match = False` review-fallback candidates ranked by threshold distance and composite score. Strict filter logic remains unchanged.

## Validation
- Six preset sheets generated.
- Peer comparison contains exactly 11 sheets.
- Peer percentile table contains 560 rows for 56 assigned companies × 10 metrics at 2024-03.
- IT Services and FMCG spot checks are included in the test/report workflow.
- 14 Sprint 3 tests pass.
