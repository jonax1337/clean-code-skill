`monthly_report(rows, 2026, 12)` should no longer crash. I checked the date ranges directly but didn't run `monthly_report` itself or any tests.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Fix:**
- I added a small helper, `_first_of_month`, that rolls months past 12 into the next year.
- `month_range` now uses it for both ends of the range.
- `quarter_range` had the same bug for Q4, so it uses the helper too. Q4 would have crashed the same way.
- The magic numbers 12 and 3 are now named constants (G25), and the duplicated date construction is gone (G5).

**Checks:**
- December 2026 gives 2026-12-01 to 2027-01-01.
- January 2026 gives 2026-01-01 to 2026-02-01.
- Q4 2026 gives 2026-10-01 to 2027-01-01.
- Q1 2026 gives 2026-01-01 to 2026-04-01.

I didn't add a regression test. The repo has no test setup that I looked at, but I can add one for the December and Q4 cases if you want.