I've written the review to `REVIEW.md`. I would not merge PR 482 as it is. I only read the diff and the description. I didn't apply the patch or run the tests, so "28 passed" is unverified.

These five need fixing before merge:

1. **SQL injection:** `adminhub/search.py:105` puts the search term straight into the SQL with an f-string. Anyone who can call the admin API can run their own SQL.
2. **Audit failures are swallowed:** `adminhub/audit.py:66-67` ignores every database error. Users can be deactivated and committed with no audit entry, which defeats the compliance purpose.
3. **`pages` is wrong:** `adminhub/api.py:20` rounds down. With 5 users and `per_page=3` it returns 1 page instead of 2, so the pager would hide the last page. No test checks it.
4. **Bulk deactivation audits things that didn't happen:** it writes an entry for unknown ids, already-inactive users and duplicate ids. The count it returns can disagree with the audit rows.
5. **The audit actor comes from the request body:** `params["actor"]` can be set to any name, and a missing one crashes with `KeyError`.

The review also covers:

- bad `page` or `per_page` values causing 500s or bypassing the cap of 100
- `list_users` now returning only the first 25 users by default for any other caller
- `search` ignoring `per_page` and not returning page info
- missing tests for the above