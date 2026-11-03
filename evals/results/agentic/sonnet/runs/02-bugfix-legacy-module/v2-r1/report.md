The December crash is fixed, and all 7 tests pass, including the two new ones.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it.

**Same bug in Q4:** `quarter_range` had the same problem for the fourth quarter, so `quarterly_report(rows, 2026, 4)` would have crashed too. It now uses the same helper.

**Tests:** I added regression tests in `tests/test_periods.py` for December and for Q4. Both expect the range to end on 2027-01-01.

I didn't change `reports/sales.py`.