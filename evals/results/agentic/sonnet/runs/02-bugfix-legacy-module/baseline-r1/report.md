I fixed the December crash in `reports/periods.py`. `month_range` built the end of the range as `datetime.date(year, month + 1, 1)`, which fails for month 13. For December it now returns January 1 of the next year.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. I fixed it too.

I ran the range functions directly and they return the right dates:
- `month_range(2026, 12)` gives 2026-12-01 to 2027-01-01.
- `quarter_range(2026, 4)` gives 2026-10-01 to 2027-01-01.
- `month_range(2026, 11)` still gives 2026-11-01 to 2026-12-01.

I did not run `monthly_report` or `quarterly_report` themselves, and I didn't add a test.