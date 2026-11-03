I've written the review to `REVIEW.md`. My verdict is that I wouldn't merge PR 482 as it is. I only read the patch and description. I didn't apply it or run the tests, so "28 passed" is dana's claim.

Blocking issues:
1. **SQL injection:** `search_users` builds its query with an f-string from the `q` parameter (`adminhub/search.py`, diff line 105). It needs bound parameters.
2. **Audit failures are swallowed:** `audit.record` catches `sqlite3.Error` and does nothing (`adminhub/audit.py`, diff lines 66-67). Users can be deactivated with no audit row and no error.
3. **False audit entries:** `deactivate_users` writes an audit row for every requested id, including unknown or already-inactive ones.
4. **Spoofable actor:** `actor` comes from the request params (`adminhub/api.py`, diff line 40), so a caller can attribute deactivations to anyone. A missing `actor` also gives a 500.

Other findings:
- **Wrong page count:** `pages` rounds down (`count // per_page`), so 5 users at 3 per page reports 1 page instead of 2. The pager would hide the last page.
- **Missing input validation:** `per_page=0` crashes, negative values slip through, and non-numeric input gives a 500.
- **`search` differs from the description:** it ignores `per_page` and doesn't return `page` or `pages`.
- **Smaller points:** there's no cap on bulk size, the single-user deactivation isn't audited, and `list_users` now returns only 25 users by default.
- **Cleanup and tests:** there's an unused import and a leftover TODO. The tests only cover happy paths.

The fixes are small, so a quick re-review after items 1–6 should be enough.