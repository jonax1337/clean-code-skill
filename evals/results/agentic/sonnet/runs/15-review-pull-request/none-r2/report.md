I've written the review to `REVIEW.md`. I wouldn't merge PR 482 as it is. I only read the diff and description and didn't run the tests, so the "28 passed" claim is unverified.

Two problems should block the merge:
1. **SQL injection in search** (`adminhub/search.py:105`): the search term is put into the SQL with an f-string. It should use bound parameters.
2. **Audit failures are swallowed** (`adminhub/audit.py:66-67`): if an audit insert fails, the deactivations still commit with no audit rows. That defeats the compliance requirement the PR exists for.

Four more bugs should also be fixed before merge:
- **Page count:** `pages` rounds down (`api.py:20`). With 5 users and `per_page=3` it returns 1 instead of 2, so the pager would hide the last page.
- **Paging input:** `per_page=0` raises a division-by-zero error. `page=0` and non-numeric values aren't validated either.
- **Bulk deactivation:** it writes audit rows for ids that don't exist, were already inactive, or are duplicated.
- **Actor:** it is read from the request body, so a caller can claim to be anyone in the audit trail.

`REVIEW.md` also lists smaller points and the test gaps, such as no check on the `page` or `pages` values and no hostile-input test.

Most of these are small fixes, so dana could probably turn them around today.