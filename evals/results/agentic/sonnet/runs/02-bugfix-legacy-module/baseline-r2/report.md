I fixed the December crash in `reports/periods.py`. I haven't run anything, so the fix is untested.

The cause was in `month_range`. It built the end of the range as `date(year, month + 1, 1)`, which is month 13 for December. It now uses January 1 of the next year when `month == 12`.

`quarter_range` had the same bug for Q4, because `3 * 4 + 1` is also 13. I fixed it the same way, so `quarterly_report(rows, 2026, 4)` would have crashed as well.