I fixed the crash: `monthly_report(rows, 2026, 12)` now returns the December report. I ran `python -m pytest -q` and all 8 tests pass, including the 3 new ones.

**Cause:** in `reports/periods.py`, `month_range` built the end of the range as `datetime.date(year, month + 1, 1)`. For December that is month 13, which raised the `ValueError`.

**Fix:** a small helper, `_first_of_month`, rolls month 13 over to January of the next year. `month_range` now uses it, so December ends on 2027-01-01.

**Same bug in Q4:** `quarter_range` had the same problem (`3 * quarter + 1` is 13 for quarter 4), so `quarterly_report` would have crashed for Q4. I fixed it with the same helper.

**New tests:**
- `month_range(2026, 12)`
- `quarter_range(2026, 4)`
- A December `monthly_report` test. It checks that Dec 1 and Dec 31 count, while Nov 30 and Jan 1 don't.