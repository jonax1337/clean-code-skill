I'd hold off on merging PR 482. I've written the review to `REVIEW.md` in the repo root, with findings ordered by importance and a verdict at the end.

I applied the patch to a temporary copy of the repo. The tests pass there (28 passed), but I reproduced each of these by calling the handlers directly:

1. **SQL injection in search** (`adminhub/search.py:13`): the search term is pasted straight into the SQL. Searching for `zzz%' OR 1=1 OR name LIKE '` returns every user, and a name with an apostrophe like `O'Brien` crashes the endpoint.
2. **Audit errors are thrown away** (`adminhub/audit.py:15-16`): an `except sqlite3.Error: pass` means that if writing the audit entry fails, the deactivation is still saved with no record. With the `audit_log` table removed, bulk deactivation still returned 200 and nothing was logged.
3. **The audit log records deactivations that didn't happen** (`users.py:62-63`): every requested id gets an entry, even unknown ones. Deactivating ids 2 and 99 reported 1 change but logged both.
4. **Single-user deactivation still isn't audited**, which goes against the "every deactivation" requirement in the PR description.
5. **The page count is wrong** (`api.py:37`): it rounds down, so 5 users at 2 per page gives 2 pages instead of 3, and at 10 per page gives 0.
6. **Bad input crashes the handlers instead of returning 400**: `per_page=0` divides by zero, non-numeric values raise errors, and `per_page=-1` returns every user, getting around the 100 cap. A missing `actor` also crashes bulk deactivation. The review also asks where `actor` comes from: if it's taken from the request rather than the logged-in session, any caller can put any name in the audit trail.

The review also covers smaller points:
- `list_users` now returns only the first 25 users by default, which breaks existing callers, and the README wasn't updated.
- Search ignores `per_page` and doesn't return a page count, though the PR says it's "paged the same way".
- An unused import, a TODO comment, some duplicated constants, and missing tests for the cases above.

None of the fixes are big, so this should be quick to turn around for the console team.