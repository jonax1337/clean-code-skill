December no longer crashes. The cause was in `reports/periods.py`: `month_range` built the end of the range as `date(year, month + 1, 1)`, which is month 13 for December.

I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. `month_range` now uses it.

`quarter_range` had the same bug for Q4, because its end date also landed on month 13. I switched it to the same helper, so `quarterly_report(rows, 2026, 4)` is fixed too.

I checked the ranges directly:
- December 2026 now gives 2026-12-01 to 2027-01-01.
- Q4 2026 gives 2026-10-01 to 2027-01-01.
- January still gives 2026-01-01 to 2026-02-01.

I didn't run `monthly_report` itself or any test suite, and I didn't add a regression test for December or Q4.