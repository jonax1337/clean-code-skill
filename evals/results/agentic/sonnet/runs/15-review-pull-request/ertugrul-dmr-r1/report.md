I've written the review to `REVIEW.md`. I would not merge PR 482 as it is.

The patch applies cleanly and the 28 tests pass, but the tests only cover the happy path. Three problems block the merge:

1. **SQL injection:** `search.py:12-13` puts the search term straight into the SQL with an f-string. It should be a bound parameter, and `%` and `_` should be escaped.
2. **Lost audit entries:** `audit.py:15-16` catches `sqlite3.Error` and ignores it. A failed audit insert still lets the deactivation commit, which breaks the compliance requirement and the rollback in `users.py`.
3. **Wrong page count:** `api.py:37` computes `count // per_page`, which rounds down. With 5 users and `per_page=3` the pager shows 1 page, so the last 2 users can't be reached. The new test never checks `pages`.

I also flagged these, in order of importance:
- The audit `actor` is taken from the request, so callers can spoof it.
- Bulk deactivation audits ids that weren't changed, including unknown, already-inactive and duplicate ones.
- Bad paging or id input gives a 500 or bypasses the page-size cap.
- `search` doesn't return `page` or `pages`.
- There is duplicated paging code, an unused `import os`, and gaps in the tests.

The three blockers are small local fixes, so a quick follow-up commit should make it mergeable today.