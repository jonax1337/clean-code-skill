I fixed the December crash in `reports/periods.py`. `month_range(2026, 12)` now returns `(2026-12-01, 2027-01-01)`.

**Cause:** `month_range` built its end date as `datetime.date(year, month + 1, 1)`. For December that is month 13, so it raised `ValueError`.

**Same bug elsewhere:** `quarter_range` had it for Q4, so `quarterly_report(rows, year, 4)` would have crashed too. I fixed that as well.

**Change:**
- I added a `_first_of_month_after(year, month)` helper that rolls over to January of the next year after December. Both range functions use it, so the logic isn't duplicated (G5).
- I replaced the bare `3` and `12` with `MONTHS_PER_QUARTER` and `MONTHS_PER_YEAR` (G25).

**Check:** I ran the range functions directly. December, January, Q4 and Q1 all return the expected dates. I didn't run `monthly_report` on real rows or look for a test suite.