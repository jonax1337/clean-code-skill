The December report no longer crashes. `monthly_report(rows, 2026, 12)` now covers 2026-12-01 up to 2027-01-01. All 7 tests pass, including the two new ones.

The bug was in `month_range` in `reports/periods.py`. It built the end date as `datetime.date(year, month + 1, 1)`, which is month 13 in December. `quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too. I fixed both with a small helper, `_first_of_month`, that rolls month 13 over to January of the next year.

I added regression tests for December and Q4 in `tests/test_periods.py`.