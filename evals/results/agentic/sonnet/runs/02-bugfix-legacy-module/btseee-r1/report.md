The December crash is fixed. All 7 tests pass, including two new ones that failed before the fix.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it for both ends of the range, so December 2026 runs from 2026-12-01 to 2027-01-01.

**Also fixed:** `quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. It was the same defect in the same file, so I fixed it with the same helper.

**Tests:** I added `test_month_range_december_rolls_into_next_year` and `test_quarter_range_fourth_quarter_rolls_into_next_year` to `tests/test_periods.py`. I ran the suite but did not run `monthly_report` on real data. Nothing is committed.