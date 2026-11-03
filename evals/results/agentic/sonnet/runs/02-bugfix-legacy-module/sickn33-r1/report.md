The December crash is fixed. `monthly_report(rows, 2026, 12)` now returns a result instead of raising.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that asks for month 13, which raised the `ValueError`.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too. I switched it to the same helper.

**Check:** I ran it in Python rather than adding a test.
- `month_range(2026, 12)` returns `(2026-12-01, 2027-01-01)`.
- `quarter_range(2026, 4)` returns `(2026-10-01, 2027-01-01)`.
- `month_range(2026, 11)` still returns `(2026-11-01, 2026-12-01)`.
- `monthly_report` on a sample row dated 2026-12-31 returns 1 order and 5 cents for `2026-12`.

I didn't add a regression test.