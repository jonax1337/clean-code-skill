I fixed the December crash. `month_range` built the end of the range as `datetime.date(year, month + 1, 1)`, and month 13 doesn't exist. It now rolls over to January of the next year. The change is in `reports/periods.py`.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. I fixed it with the same helper, `_first_of_month_after`.

I added regression tests in `tests/test_periods.py` for December and for Q4. I didn't run them against the old code first. `python -m pytest -q` gives 7 passed.

I did not call `monthly_report(rows, 2026, 12)` itself. The new tests only cover the two range functions it relies on.