The December crash is fixed. `monthly_report(rows, 2026, 12)` should no longer raise. I didn't call it directly, but the new `month_range` test covers the failing case. The full suite passes (7 tests).

The cause was in `month_range` in `reports/periods.py`. It built the end of the range as `datetime.date(year, month + 1, 1)`, which fails for month 13. For December it now returns January 1 of the next year.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too. I fixed that the same way.

I added a regression test for each case in `tests/test_periods.py`: December and Q4 both roll into the next year.