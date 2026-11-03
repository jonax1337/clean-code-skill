The December report no longer crashes. `monthly_report(rows, 2026, 12)` now covers 2026-12-01 up to 2027-01-01. I ran `month_range` and `quarter_range` by hand for December, January, Q4 and Q1, and the existing 5 tests pass. I didn't add a test for the December or Q4 case.

**Cause:** `month_range` built the end of the range as `date(year, month + 1, 1)`, which is month 13 in December. `quarter_range` had the same bug for Q4, so the Q4 quarterly report would have crashed too. I fixed both in `reports/periods.py`.

**Fix:** Both functions now use one small helper, `_first_of_month`. It rolls months past 12 into the next year. I also replaced the magic numbers `12` and `3` with named constants.