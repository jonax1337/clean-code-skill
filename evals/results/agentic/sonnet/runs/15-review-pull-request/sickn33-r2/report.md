I've written the review to `REVIEW.md`. I would not merge PR 482 as it is. I only read the diff and description. I didn't apply the patch or run the tests, so I haven't checked the "28 passed" claim.

The five blocking findings:
1. **SQL injection** in `search.py:13`: the search term is put into the SQL with an f-string. It should be a bound parameter.
2. **Silent audit loss** in `audit.py:10-16`: `record()` swallows database errors, so deactivations can be committed with no audit row. That defeats the compliance requirement. The existing single-user deactivation isn't audited at all.
3. **Forgeable audit actor** in `api.py:62`: the actor comes from the request body, so the caller can claim to be anyone. A missing key also causes a 500.
4. **Wrong page count** in `api.py:37`: `pages` uses floor division, so 5 users gives 0 pages and a partial last page is dropped. That breaks the pager the console team is waiting for.
5. **Unvalidated paging input** in `api.py:35-36`: `per_page=0` crashes, and a negative `per_page` bypasses the 100 cap because SQLite treats `LIMIT -1` as unlimited. Bad page values and non-numeric input also cause errors.

The review also covers lower-priority items: bulk deactivation differs from the single-user path (unknown, duplicate and already-inactive ids), `search` returns no `page`/`pages`, `list_users` is now capped at 25 by default, and there are some minor cleanups and test gaps.

The fixes for items 1 to 5 are small and local.