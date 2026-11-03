I fixed the December crash. `monthly_report(rows, 2026, 12)` now returns a normal report. I checked it with a sample December 31 order, which was counted. I didn't run a test suite.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which `datetime` rejects.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it. December 2026 gives the range 2026-12-01 up to 2027-01-01.

**Q4 had the same bug:** `quarter_range` used the same pattern, so `quarterly_report(rows, year, 4)` would have crashed too. I switched it to the helper as well. Q4 2026 now gives 2026-10-01 up to 2027-01-01.

Months 1–11 give the same ranges as before. I didn't add a regression test because I didn't see a test setup. If you'd like one, I can add tests for December and Q4.