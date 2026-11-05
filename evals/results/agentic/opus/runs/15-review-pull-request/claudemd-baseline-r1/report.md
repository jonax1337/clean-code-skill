I wrote the review to `REVIEW.md`. I wouldn't merge PR 482 as it is.

I applied the patch to a separate copy of the repo and ran the tests: 28 passed, as the PR says. The tests just don't check the problems below. I confirmed most findings with small scripts; the first one I found by reading the code.

**Blocking:**
1. **SQL injection** in `adminhub/search.py:13`. The `q` search term is pasted straight into the SQL text. This goes against the README's "always use `?` placeholders" rule, and a name with an apostrophe would also break search. One of my checks on this was stopped by a safety filter, so I didn't test it any further. The code makes the problem clear.
2. **Audit errors are silently ignored** (`adminhub/audit.py:15-16`). With the `audit_log` table missing, users were still deactivated and no audit row was written. The undo-on-error code in `deactivate_users` never runs.
3. **The audit log records things that didn't happen** (`adminhub/users.py:160-162`). Deactivating ids `[2, 99, 2]` reported 1 user deactivated but wrote audit rows for 2, 99 and 2 again. Users who were already inactive are also counted and logged again.
4. **The page count is wrong** (`adminhub/api.py:37`). It rounds down, so 5 users at 3 per page gives 1 page instead of 2, and 5 users at the default page size gives 0 pages.

**Should fix:**
- Bad paging input crashes instead of returning a 400 error: `per_page=0` divides by zero, and a non-number fails. Page 0 or a negative page isn't rejected.
- A bulk deactivation without an `actor` crashes.
- The actor name comes from the client, so a caller can claim to be anyone in the audit log.
- Search ignores `per_page` and doesn't return `page`/`pages`, though the PR description says it does.

There are also a few minor points in the file (an unused import, the README not updated) and a list of missing tests. The fixes are all small, so the PR should be ready soon after.

I only added `REVIEW.md` to the repo and removed the temporary copy and scripts afterwards.