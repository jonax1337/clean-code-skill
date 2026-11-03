I've written the review to `REVIEW.md`. My recommendation is **don't merge it as it is**. The fixes are small, though, so a quick second round should be enough.

The most important problems, all of which I reproduced:

1. **SQL injection in search** (`adminhub/search.py:13`). The search term is pasted straight into the SQL. Searching for `zzz' OR 1=1 OR name LIKE '` returns every user, and an ordinary name like `O'Brien` makes the request fail with an error.
2. **Audit failures are silently ignored** (`adminhub/audit.py:10-16`). When I removed the `audit_log` table, the bulk deactivation still succeeded and returned 200, but nothing was written to the audit log. That goes against the compliance requirement the PR is built for.
3. **The audit log records deactivations that never happened** (`adminhub/users.py:62-64`). Every requested ID gets an entry: deactivating `[1, 99]` reports 1 deactivated but logs both 1 and 99.
4. **The page count is wrong** (`adminhub/api.py:37`). It rounds down, so 5 users at 10 per page reports 0 pages and the new pager shows nothing.
5. **Bad input causes server errors instead of 400s.** For example: `per_page=0` crashes, a missing `actor` crashes, and `per_page=-1` returns all users.

Under "should fix" I also noted:
- **`list_users` behavior change:** it now returns only 25 users unless the caller asks for more pages.
- **Search paging doesn't match the description:** it ignores `per_page` and doesn't return `page`/`pages`.
- **The README is outdated:** it doesn't list the new handlers or the new `list_users` parameters.

There is one open question for you: whether the web layer sets `actor` from the logged-in user. Right now it comes from the request parameters, so a client might be able to put any name into the audit log.

**How I checked:** I applied the patch in a separate copy of the repo and ran the tests: `python -m pytest -q` gives 28 passed, as the PR says, but no test covers any of the problems above. I then ran a short script against an in-memory database for each finding, and deleted the copy afterwards. Your working tree only has the new `REVIEW.md`.