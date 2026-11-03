I wrote the review to `REVIEW.md` in the repo root. I wouldn't merge PR 482 as it is.

I read the diff, the description, the README and the current `api.py`, `db.py` and `conftest.py`. I didn't apply the patch or run the tests, so the PR's "28 passed" is unchecked. The line numbers in the review refer to lines of `pr/482.diff`, since the patch isn't applied.

The findings that matter most, in order:
1. **SQL injection:** `search.py` builds the `LIKE` query with an f-string around the request parameter `q`. The README says all queries use `?` placeholders.
2. **Audit log hides failures:** `audit.record` catches `sqlite3.Error` and ignores it. A failed audit insert still lets the deactivations commit, which defeats the compliance reason for the feature.
3. **Audit gaps:**
   - The existing single-user `deactivate_user` writes no audit entry.
   - The bulk path audits every id in the request, including unknown and already-inactive users.
4. **Forgeable actor:** The audit `actor` comes from the request body, so the log can be forged, and a missing `actor` gives a 500.
5. **Wrong page count:** `pages = count // per_page` rounds down. Five users with `per_page=3` reports 1 page instead of 2, which would hide the last page in the pager.
6. **Unvalidated paging input:** `page=abc` gives a 500, `per_page=0` divides by zero, and `per_page=-1` returns every row.
7. **Silent breaking change:** `list_users` now returns 25 users by default, but the README documents it as returning all users.

The review also lists smaller items: unchecked bulk input, duplicated paging logic, an unused `import os` and a stray TODO. It names the missing tests and notes what is good in the PR. The SQL injection and the audit-log failure handling are small fixes.