I fixed the December crash, and the full test suite now passes (`pytest`: 7 passed). I didn't run the new tests against the old code first, so I haven't seen them fail.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Fix:** I added a small helper, `_add_months`, that rolls over into the next year. `month_range` now uses it, so December ends on 1 January of the following year.

**Same bug in Q4:** `quarter_range` had the same flaw, since Q4 ended at month 13, so `quarterly_report(rows, year, 4)` would have crashed too. I fixed it with the same helper.

**Tests:** I added a December test for `month_range` and a Q4 test for `quarter_range` in `tests/test_periods.py`.

I left `reports/sales.py` alone. It repeats the same date filter in `sum_in_range` and in the order count, but that isn't part of this bug.