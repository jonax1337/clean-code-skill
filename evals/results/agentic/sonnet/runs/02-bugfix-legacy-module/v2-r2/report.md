The December crash is fixed, and all 7 tests pass, including the new ones.

`month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`. I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year, and `month_range` now uses it.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, year, 4)` would have crashed the same way. I changed it to use the helper too.

I added regression tests in `tests/test_periods.py` for December and Q4. I didn't run your original `monthly_report(rows, 2026, 12)` call on real rows.