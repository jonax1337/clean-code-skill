I fixed the December crash, but I haven't run it or any tests.

The cause was in `month_range` in `reports/periods.py`. It built the end of the range as `datetime.date(year, month + 1, 1)`, which is month 13 for December. It now uses January 1 of the next year when the month is 12.

`quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed the same way. I applied the same fix there.