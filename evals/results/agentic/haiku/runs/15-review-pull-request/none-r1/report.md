I wrote the review to `REVIEW.md` in the repo root. **I would not merge PR 482 as it is.**

The most serious problems:

1. **SQL injection in search** (`adminhub/search.py:13`). The search term is interpolated into the SQL with an f-string, and the handler passes `q` straight from the request. The tests only use plain words, so nothing catches it. This needs a parameterized query.
2. **Audit failures are swallowed** (`adminhub/audit.py:15-16`). `except sqlite3.Error: pass` lets the bulk deactivation commit even when the audit row was not written, which defeats the compliance requirement the PR is for.
3. **Wrong page count** (`adminhub/api.py:37`). Floor division drops the last partial page; 5 users at 2 per page reports 2 pages instead of 3. The console's pager can't reach the last page.

The review also covers unvalidated `page`/`per_page` (a `per_page=0` divides by zero, bad input gives a 500), audit entries written for unknown or duplicate ids, a required `actor` taken from the client, and a breaking change where `list_users` now returns one page by default without that being mentioned in the description.

Caveats: I didn't check out the branch or run the test suite, so the "28 passed" claim is unverified. Line numbers are derived from the diff hunk headers, so they may be off by a line. I also didn't confirm the README's "pages start at 1" claim.