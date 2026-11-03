I wrote the review to `REVIEW.md` in the repo root. My answer is **don't merge PR 482 as it is.**

The patch applies cleanly. The suite passes with 28 tests, as the PR says. I ran it in a scratch copy and left your working tree untouched. The probes below ran against that copy.

**Blockers**
1. **SQL injection in `search_users`** (`adminhub/search.py:13`). The search term goes into the SQL through an f-string. The README says all queries use `?` placeholders. A term containing `' --` changed the statement's structure, and the call failed with a binding error. Any caller who controls `q` can rewrite the query.
2. **Audit failures are swallowed** (`adminhub/audit.py:15-16`). With the `audit_log` table dropped, bulk deactivation still returned 200 and deactivated the user with no audit row. The compliance requirement is that every deactivation is recorded, so a failed audit write should fail and roll back the operation.
3. **Single-user deactivation is not audited** (`users.py:47-52`, `api.py:50-57`). Only the bulk path writes to the trail. Compliance should confirm whether that is in scope.

**Also fix before merging**
4. **The audit `actor` comes from request params** (`api.py:62`). Unless the web layer overwrites it with the authenticated user, any client can write any actor name. The web layer isn't in this repo, so I couldn't check this.
5. **The page count is wrong** (`api.py:37`). It uses floor division, so 5 users at `per_page=2` gives 2 pages instead of 3. The pager the console team is waiting for would be unable to reach the last page.
6. **Bad paging input crashes or misbehaves**. `per_page=0` raises `ZeroDivisionError`. `page=0` is silently treated as page 1. A missing `actor` raises `KeyError`, and non-integer values raise `ValueError`.

The review also covers lower-priority items: bulk deactivation audits IDs that matched no user, the `IN (...)` list has no cap, there are magic numbers and an unused import, the README is stale, and some tests are missing. Each finding has its file and line and the rule it breaks from the Clean Code skill.

I didn't change any code, since you asked only for a review. The fixes are mostly small. The injection fix and the audit change are the ones I'd make first.