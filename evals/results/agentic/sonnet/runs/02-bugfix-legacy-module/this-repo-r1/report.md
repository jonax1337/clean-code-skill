December reports no longer crash. `monthly_report(rows, 2026, 12)` now covers 2026-12-01 up to but not including 2027-01-01. `pytest` passes with 9 tests, and I ran it after my last edit.

**Cause:** in `reports/periods.py`, `month_range` built the end of the range as `datetime.date(year, month + 1, 1)`, which is month 13 for December.

**Same bug in Q4:** `quarter_range` had the same problem for quarter 4, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. I fixed it too.

**Fix:** a small helper, `_first_of_month`, rolls a month past 12 into January of the next year. Both range functions now use it.

**Tests added:**
- `tests/test_periods.py`: December and Q4 ranges end on 1 January of the next year.
- `tests/test_sales.py`: the December and Q4 reports include 31 December and exclude 1 January of the next year.

I left `week_range` and the report functions alone.