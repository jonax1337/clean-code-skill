The December crash is fixed. `pytest` now shows 9 passed. I didn't run a linter or type checker.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raises the `ValueError`. `quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. Both range functions now use it.

**Tests added:**
- `month_range` and `quarter_range` for December and Q4, in `tests/test_periods.py`.
- `monthly_report` for December and `quarterly_report` for Q4, in `tests/test_sales.py`. Each checks that 31 December is counted and that 30 November and 1 January are not.

I didn't touch `week_range` or the report functions. Neither needed changes.