I fixed the December crash. `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`, which is month 13 in December. It now rolls over to January 1 of the next year.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, year, 4)` would have crashed too. I fixed it the same way.

I checked the date ranges directly, but I didn't run `monthly_report` on real rows or any test suite:
- `month_range(2026, 12)` returns 2026-12-01 to 2027-01-01.
- `quarter_range(2026, 4)` returns 2026-10-01 to 2027-01-01.
- `month_range(2026, 11)` still returns 2026-11-01 to 2026-12-01.