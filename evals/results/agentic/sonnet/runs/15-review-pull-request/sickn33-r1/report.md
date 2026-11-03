I wrote the review to `REVIEW.md`, and I wouldn't merge PR 482 as it is.

I applied the patch in a scratch copy and the 28 tests pass, as the description says. I then reproduced the main problems directly; the scratch copy is deleted again.

Four findings block the merge:
1. **SQL injection in search** (`search.py:13`): the `q` parameter is put into the SQL with an f-string. A quote in the input changes the query. `%` also matches every user.
2. **Audit failures are hidden** (`audit.py:15-16`): `record()` swallows database errors. With the audit table missing, bulk deactivation still returned 200 and deactivated the user, with nothing logged.
3. **Actor comes from the request body** (`api.py:62`): anyone can attribute a deactivation to someone else, and a missing `actor` gives a 500.
4. **Bulk audit entries don't match what changed** (`users.py:61-63`): with ids `[1, 999]`, one user was deactivated but both ids were logged.

Smaller problems:
- The `pages` count is rounded down (5 users at 2 per page gives 2 pages instead of 3), so the pager would hide the last user.
- `per_page=0` crashes, and bad paging values give a 500 instead of a 400.
- The user list now silently returns only 25 users by default.
- Single-user deactivation isn't audited.

The review also lists minor items and the tests that are missing.

The pager work is close to ready once the `pages` count, input validation and the default-25 change are sorted out. If the console team is waiting on it, you could split it out and merge search and bulk deactivation separately.