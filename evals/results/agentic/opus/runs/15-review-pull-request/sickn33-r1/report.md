I wrote the review to `REVIEW.md`. **I wouldn't merge this as it is.** The test suite passes (28 passed, matching the description), but those tests don't cover any of the problems below. I applied the patch in a temporary copy of the repo and called the new functions with bad and edge-case input to confirm them.

The main problems, most important first:

1. **SQL injection in search** (`adminhub/search.py:13`): the search term is pasted straight into the query text. Searching for `zzz' OR 1=1 OR name LIKE '` returns every user. A plain apostrophe, as in `o'brien`, makes the search crash with a server error.
2. **Failed audit writes are silently ignored** (`adminhub/audit.py:15-16`): because the error is swallowed, the rollback in `deactivate_users` never runs. With the audit table missing, bulk deactivation still returns success and deactivates the users, but logs nothing.
3. **The audit log records deactivations that didn't happen** (`adminhub/users.py:61-63`): an id that doesn't exist gets an audit entry, and so does deactivating someone who is already inactive. The returned count is wrong in the same cases.
4. **The page count is wrong** (`adminhub/api.py:37`): it rounds down. With 5 users and 10 per page it reports 0 pages; with 2 per page it reports 2 instead of 3. A page size of 0 crashes it.
5. **Bad input causes server errors instead of "bad request" errors**: a non-numeric page or id, or a missing `actor`, crashes the handler. A page size of -1 returns every row and gets around the cap of 100.

Also worth fixing:
- `list_users` now returns only the first 25 users by default, but the README still says it returns all of them.
- Search isn't paged like the user list, despite what the description says: it ignores the page size and doesn't return page information.
- It's unclear whether `actor` comes from the logged-in session or from the client. If the client sends it, anyone can put any name in the compliance log.

Each fix is a few lines plus a test, so a revised PR could still land today. If that's too tight, the user-list paging could go out first once problems 4 and 5 are fixed. I haven't committed `REVIEW.md`.