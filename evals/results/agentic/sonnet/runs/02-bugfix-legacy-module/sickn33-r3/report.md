I fixed the December crash in `reports/periods.py`. `month_range(2026, 12)` now returns `(2026-12-01, 2027-01-01)`, so `monthly_report(rows, 2026, 12)` no longer raises.

`month_range` built the end of the range as `date(year, month + 1, 1)`, which is month 13 for December. I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year, and `month_range` now uses it.

`quarter_range` had the same bug for Q4, so the Q4 quarterly report would have crashed too. I fixed it the same way. `quarter_range(2026, 4)` now returns `(2026-10-01, 2027-01-01)`.

I checked the date ranges directly: December, Q4 and January all return the expected values. I didn't run `monthly_report` itself or any test suite.