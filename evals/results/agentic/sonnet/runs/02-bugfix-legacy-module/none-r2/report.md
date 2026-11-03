The December report no longer crashes. `monthly_report(rows, 2026, 12)` now uses 2026-12-01 to 2027-01-01 as its range.

The cause was in `reports/periods.py`. `month_range` built the end date as `month + 1`, which is month 13 in December. It now rolls over to January of the next year.

`quarter_range` had the same bug for Q4, so `quarterly_report` would have crashed too. I fixed that the same way.

I only ran `month_range` and `quarter_range` directly. They return the right ranges for December (to 2027-01-01), Q4 (2026-10-01 to 2027-01-01) and March (unchanged). I didn't run `monthly_report` or any test suite. I haven't committed anything.