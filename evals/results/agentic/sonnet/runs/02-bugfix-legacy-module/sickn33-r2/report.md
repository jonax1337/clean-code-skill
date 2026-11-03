I fixed the December crash. The cause was in `reports/periods.py`: `month_range` built the end of the range as `month + 1`, which is month 13 in December and raised the `ValueError`.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too. Both now use a small helper, `_first_of_month_after`, which rolls December over to January of the next year.

I ran the range functions directly and they return the right boundaries:
- `month_range(2026, 12)` gives 2026-12-01 to 2027-01-01.
- `quarter_range(2026, 4)` gives 2026-10-01 to 2027-01-01.
- `month_range(2026, 3)` still gives 2026-03-01 to 2026-04-01.

I didn't run `monthly_report` itself or add a regression test.