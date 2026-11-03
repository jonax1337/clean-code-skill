The December crash is fixed, and all 7 tests pass. I committed it as `b3272b6` on `main` but haven't pushed it.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. In December that is month 13, which `datetime` rejects. `quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` would have crashed too.

**Fix:** a small helper, `_first_of_month`, rolls month 13 into January of the next year. Both functions now use it, so that logic lives in one place.

**Log of what I did:**
1. Read `sales.py` and `periods.py` and found the month-13 construction.
2. Added two regression tests, for December and Q4. Both failed with the same `ValueError` as your traceback.
3. Added the helper and switched both range functions to it. The full suite then passed.
4. Committed the change.

I skipped the crapper, dryer and mutator passes. The change is a few lines in one file, and the helper's `// 12` / `% 12` arithmetic is covered by the two new tests (the rollover case) and the existing ones (non-rollover).

Git warned that CRLF line endings in `periods.py` will be converted to LF. That's a line-ending setting in your repo, not something I changed on purpose.

I didn't push, since you didn't ask me to. Do you want me to push to `main`?