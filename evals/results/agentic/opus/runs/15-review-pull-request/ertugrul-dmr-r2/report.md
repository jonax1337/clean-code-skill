I've written the review to `REVIEW.md`. My recommendation is **not to merge PR 482 as it is.** The test suite does pass (28 passed, as the description says), but I applied the patch to a scratch copy and called the new handlers with unusual inputs, and that turned up these problems:

1. **SQL injection in the new search** (`adminhub/search.py:13`). The search term is put straight into the SQL text instead of being passed as a parameter. A query like `zzz' OR 1=1 OR name LIKE '` returns every user. An ordinary name like `O'Brien` crashes it with a 500 error.
2. **Audit writes can fail without anyone knowing** (`adminhub/audit.py:15-16`). Errors from the audit insert are caught and ignored, so the rollback never happens. I deleted the `audit_log` table and bulk deactivation still returned 200 and deactivated the user.
3. **The audit trail is inaccurate** (`adminhub/users.py:62-63`). It writes a row for every requested id, not for each user who actually changed. An unknown id gets logged as deactivated, and a repeated id gets logged twice. The existing single-user `deactivate_user` writes no audit row at all, so "every deactivation is audited" isn't met.
4. **Wrong page count** (`adminhub/api.py:37`). It rounds down: 5 users at 2 per page reports 2 pages instead of 3. With fewer than 25 users it reports 0 pages. No test checks this value.

There are smaller issues too:
- **Bad input gives 500s:** `per_page=0`, non-numeric ids or pages, or a missing `actor` crash instead of returning 400. `per_page=-1` gets around the 100 cap.
- **`list_users` now returns at most 25 users by default.** The README wasn't updated for that or for the new handlers.
- **Search isn't paged like the list:** it ignores `per_page` and doesn't return `page`/`pages`.
- **Leftovers:** an unused import, a magic number, and gaps in the tests.

Each fix is small, so a revised PR could still go in today.