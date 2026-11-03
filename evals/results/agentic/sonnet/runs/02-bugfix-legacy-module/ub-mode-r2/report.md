`monthly_report(rows, 2026, 12)` no longer crashes. All 7 tests pass, including two new ones for December and Q4. I committed the fix as `6d42fe4` on `main` and haven't pushed it.

**Cause:** `month_range` in `reports/periods.py` built the end of the range as `date(year, month + 1, 1)`. For December that is month 13, which raises the `ValueError`. `quarter_range` had the same bug for Q4, so `quarterly_report(rows, 2026, 4)` crashed too. I fixed both.

**Fix:** I added a small helper, `_first_of_month`, that rolls month 13 over to January of the next year. Both range functions now use it, so the rule lives in one place.

**Log:**
1. I read `sales.py`, `periods.py` and the existing tests, and found the same bug in `quarter_range`.
2. I added December and Q4 tests, each with a row on the year boundary. Both failed with the reported error before the change.
3. I added the helper and switched both range functions to it. The full suite then passed.
4. I committed with the reason and the proof.

I skipped the crapper, dryer and mutator passes. The change is a few lines and doesn't add any branching.