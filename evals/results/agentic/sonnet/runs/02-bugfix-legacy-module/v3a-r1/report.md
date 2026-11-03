I fixed the December crash, and all 7 tests pass (`pytest`).

**Cause:** `month_range` in `reports/periods.py` built the end date as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Changes:**
- `month_range` now rolls over into January of the next year after December.
- `quarter_range` had the same bug for Q4, which would have crashed `quarterly_report(rows, 2026, 4)`. It now takes its end date from `month_range(year, 3 * quarter)`.
- I added two regression tests in `tests/test_periods.py`, one for December and one for Q4. I didn't run them against the old code to confirm they fail there.

I didn't change `reports/sales.py`.