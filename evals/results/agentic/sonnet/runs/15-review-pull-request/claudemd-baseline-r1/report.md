I've written the review to `REVIEW.md`. My verdict is that I would not merge PR 482 as it is. I only read the patch and the description; I didn't apply it or run the tests, so the "28 passed" claim is untested.

The main findings, most important first:
1. **SQL injection:** `adminhub/search.py:13` puts the search term straight into the SQL with an f-string. The term should be passed as a bound parameter instead.
2. **Audit failures are swallowed:** `adminhub/audit.py:15-16` catches the database error and ignores it. A deactivation can then be committed with no audit row, which defeats the compliance requirement.
3. **Wrong page count:** `adminhub/api.py:35` rounds the page count down, so 5 users at 3 per page gives 1 page instead of 2. A `per_page` of 0 crashes, a negative `per_page` bypasses the 100 cap, and non-numeric values cause a server error.
4. **Actor comes from the request:** `bulk_deactivate` in `adminhub/api.py` takes the actor from the request, so the audit trail can be forged. A missing actor or bad ids also cause server errors.
5. **Audit rows for unchanged users:** unknown or already-inactive ids still get an audit row.

The review also covers smaller points: `search` doesn't return page counts, `list_users` now returns only 25 users by default while the README still says all, and several cases have no tests.

The pager and bulk deactivation could merge once findings 1–4 are fixed and covered by tests.