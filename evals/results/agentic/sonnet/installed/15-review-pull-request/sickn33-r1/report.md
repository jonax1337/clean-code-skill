I wrote the review to `REVIEW.md`. I would not merge PR 482 as it is. I only read the diff and the description. I didn't check out the branch or run the tests, so the "28 passed" is the author's claim.

These four need fixing before merge:

1. **SQL injection in search:** `adminhub/search.py:13` puts the search term straight into the SQL string. Any caller of the admin API can inject SQL. It should use bound parameters.
2. **Audit failures are swallowed:** `adminhub/audit.py:11-12` ignores database errors when writing the audit entry. A bulk deactivation can then succeed with no audit entry, which defeats the compliance purpose. The error should propagate so the transaction rolls back.
3. **Wrong page count:** `adminhub/api.py:20` rounds down. With the default page size of 25 and 5 users it returns 0 pages, and 5 users at 2 per page gives 2 instead of 3. The pager would be wrong.
4. **Bulk deactivation trusts the request:** `adminhub/api.py:60-61` takes the actor name from the request body, so it can be faked, and a missing actor causes a 500 error. Unknown or duplicate ids are not rejected, and unknown ids still get audit rows. The id list has no size cap.

The review also lists smaller items:
- Paging inputs aren't validated. `per_page=0` crashes, and a negative `per_page` removes the limit.
- `search` doesn't return `page` or `pages`.
- The README still says `list_users` returns all users, but it is now capped at 25.
- Single-user deactivation isn't audited.
- `search.py` has an unused import.

The tests only cover the happy paths, which is why they pass despite these problems. `REVIEW.md` lists the missing cases.