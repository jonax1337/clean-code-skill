I fixed the December crash, and all 7 tests pass (`pytest`). I added the two year-end tests after reading the code and didn't run them against the old code, so I haven't watched them fail.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which is the `ValueError` you saw.

**Fix:** Both range functions now share a small helper, `_months_range`. It works out the end date with `divmod`, so December rolls over to January of the next year.

**Same bug in Q4:** `quarter_range` had the same flaw, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. The shared helper fixes it too.

**Tests:** I added `test_month_range_rolls_over_year_end` and `test_quarter_range_rolls_over_year_end` to `tests/test_periods.py`.

I didn't touch `reports/sales.py`. Its two report functions repeat the same filtering logic, which I left alone because it's outside this bug.