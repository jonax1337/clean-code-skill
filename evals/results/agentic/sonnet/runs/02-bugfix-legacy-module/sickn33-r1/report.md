The December report no longer crashes. I checked the date ranges directly, but I didn't run `monthly_report` itself or any test suite.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `datetime.date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Same bug in Q4:** `quarter_range` did the same thing for quarter 4, so `quarterly_report(rows, 2026, 4)` would have crashed too. I fixed both.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. Both range functions now use it.

**Check:** `month_range(2026, 12)` now returns `(2026-12-01, 2027-01-01)` and `quarter_range(2026, 4)` returns `(2026-10-01, 2027-01-01)`. `month_range(2026, 1)` still returns `(2026-01-01, 2026-02-01)`.