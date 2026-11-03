The December crash is fixed. `pytest` passes with 7 tests, including the two new ones.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raises the `ValueError`.

**Changes:**
- **`month_range`:** the end date is now `date(year + month // 12, month % 12 + 1, 1)`, so December ends on 1 January of the next year.
- **`quarter_range`:** it had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too. It now builds its start and end from `month_range`.
- **Tests:** I added regression tests in `tests/test_periods.py` for December and for Q4. I didn't run them against the old code to confirm they fail there.