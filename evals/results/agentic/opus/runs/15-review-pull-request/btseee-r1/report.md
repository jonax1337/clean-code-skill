I wrote the review to `REVIEW.md`. My recommendation is **don't merge PR 482 as it is**.

I applied the patch to a temporary copy of the repo. The tests pass (28 passed, as the PR says), and I called the new handlers directly to check the cases below.

**Blocking problems:**
1. **SQL injection in search** (`adminhub/search.py:13`): the search text is pasted straight into the SQL query. An ordinary name like `O'Brien` already makes the query fail. Also, typing `_` matches every user.
2. **Failed audit writes are silently ignored** (`adminhub/audit.py:15-16`): if writing the audit entry fails, the deactivation still goes through and the caller gets a success response. I tested this by removing the audit table: the user was deactivated and nothing was logged.
3. **The audit log can contain wrong entries** (`adminhub/users.py:63-65`): it gets an entry for every id in the request, including ids that don't exist (asking for 1 and 99 deactivates one user but logs two). The `actor` name comes from the request parameters, so whoever calls the endpoint decides whose name is logged.
4. **Single-user deactivation is still not logged**, even though the PR says every deactivation should be.
5. **The page count is wrong** (`adminhub/api.py:37`): it rounds down, so 5 users at 2 per page gives 2 pages instead of 3. Any list shorter than one full page reports 0 pages. No test checks the page count.

**Should fix:** bad paging or bulk input (`per_page=0`, non-numbers, a missing `actor`) crashes the handler instead of returning a 400 error. Search doesn't page the same way as the user list. The README wasn't updated for the new parameters and handlers. There are also a few minor points: an unused import, a leftover TODO, a duplicated column list, and an existing test that now passes only by accident.

Fixes 1, 2 and 5 are small, so the console team's deadline is still reachable once 1–5 are fixed and have tests.