# Data provenance and update procedure

**Dataset:** data/labour_indicators.csv  
**Maintainer review date:** 2026-10-21  
**Publisher:** Department of Census and Statistics (DCS), Sri Lanka  
**Topic:** Sri Lanka Labour Force Survey

## Observations included

| Period | Participation | Unemployment | Official source directory |
|---|---:|---:|---|
| 2025 annual | 49.4% | 3.9% | [Annual labour-force bulletins](https://www.statistics.gov.lk/LabourForce/StaticalInformation/Bulletins/) |
| 2026 Q1 | 49.2% | 3.7% | [Quarterly labour-force reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/) |
| 2026 Q2 | 50.0% | 4.0% | [Quarterly labour-force reports](https://www.statistics.gov.lk/LabourForce/StaticalInformation/QuarterlyReports/) |

The DCS site lists the 2025 annual and 2026 Q1 results, and its latest reports list the 2026 Q2 results. The CSV stores the official DCS landing-page URL rather than a guessed direct PDF URL, so the source remains navigable if publication filenames change.

## Safe update procedure

1. Open the relevant DCS landing page and then the publication for the exact period.
2. Confirm indicator definitions, period, units and values in the publication itself; do not infer a missing value.
3. Update the CSV row and source URL together. Do not silently replace historical observations.
4. Update this document's review date and table if the dataset changes.
5. Run pytest -q and review the Git diff before merging.

## Limitations

- The CSV is a manually reviewed snapshot, not an automatically refreshed feed.
- Tests validate expected rows, ranges and official source-domain links; they do not establish that an official PDF was parsed correctly.
- FastAPI seed records are application seed data, not a live feed or continuously verified dataset.
- AI research output is not itself an official statistical source. Prefer DCS or Central Bank of Sri Lanka publications for primary economic figures.
