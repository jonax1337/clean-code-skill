The December crash is fixed. `pytest` passes with 7 tests, including the two new ones.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that asks for month 13, which raises the `ValueError`.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it.

`quarter_range` had the same bug for Q4 (month 13 again), so `quarterly_report(rows, 2026, 4)` would have crashed the same way. It now uses the helper too.

I added regression tests for both cases in `tests/test_periods.py`: `month_range(2026, 12)` and `quarter_range(2026, 4)`. Each expects an end date of 2027-01-01.

I did not run `monthly_report` against your real December data. The tests cover the date ranges, which is where the crash was.