I fixed the crash in `reports/periods.py`, but I haven't run the code or any tests.

The cause was in `month_range`. It built the end of the range as `datetime.date(year, month + 1, 1)`, which becomes month 13 for December. When the month is 12, it now uses January 1 of the next year.

`quarter_range` had the same bug for Q4, because `3 * 4 + 1` is also 13. `quarterly_report(rows, 2026, 4)` would have crashed the same way, so I fixed it too.