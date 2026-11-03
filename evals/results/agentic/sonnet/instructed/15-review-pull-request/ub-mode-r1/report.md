I wrote the review to `REVIEW.md`, and I wouldn't merge PR 482 as it is. I applied the patch in a scratch copy, where the suite passes (28 passed). The findings come from reading the code, and I haven't run any of them. I didn't change the repo apart from adding `REVIEW.md`.

Two problems should block the merge:
- **SQL injection:** `adminhub/search.py:13` builds the `LIKE` clause with an f-string, so any caller can inject SQL through `q`.
- **Lost audit entries:** `adminhub/audit.py:14-16` swallows `sqlite3.Error`, so a failed audit insert is ignored and the deactivation still commits. That defeats the compliance purpose of the log.

Four more bugs hit the features the console team is waiting for:
- **Audit rows vs. actual changes:** `users.py:62-63` audits every id passed in, including nonexistent and already-inactive users, while the returned count only covers rows that changed.
- **Single deactivation not audited:** the existing `deactivate_user` writes no audit row.
- **Wrong page count:** `api.py:37` uses floor division, so 5 users at 2 per page reports 2 pages and the last page is unreachable.
- **Unvalidated paging input:** `per_page=0` crashes with `ZeroDivisionError`, and a negative `per_page` returns every user. Non-numeric values and a missing `actor` also cause 500s.

The rest is smaller: `actor` is taken from the request body, the bulk id list has no size cap or dedupe, and there's an unused `import os` plus a leftover TODO. The tests also never check `pages`, injection, unknown ids or invalid paging input.

The fixes are small and local, so it could be mergeable today after one follow-up commit.