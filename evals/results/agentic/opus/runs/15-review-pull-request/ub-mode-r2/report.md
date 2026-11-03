I've written the review to `REVIEW.md`. My recommendation is **don't merge it as it is**.

I applied the patch to a temporary copy of the repo and the tests pass (28, as the PR says). I then called the new handlers directly with bad and edge-case inputs to check each problem.

**Blocking:**
1. **SQL injection in search** (`adminhub/search.py:13`): the search term is pasted straight into the SQL. Searching for `zzz' OR 1=1 OR name LIKE '` returns every user, and a search containing a single `'` crashes with a server error.
2. **The audit log can silently lose entries** (`adminhub/audit.py:10-16`): the audit code catches database errors and ignores them. With the audit table missing, a user was still deactivated and nothing was logged.
3. **Single-user deactivation isn't audited at all.** Only the new bulk path writes to the audit log, so "every deactivation in the audit trail" isn't met.
4. **The page count is wrong** (`adminhub/api.py:37`): it rounds down. With 5 users it reports 1 page at 3 per page, and 0 pages at the default size of 25.
5. **Bad page parameters aren't checked:**
   - `per_page=0` and non-numeric values crash with server errors instead of returning a 400.
   - `per_page=-1` gets around the 100 limit and returns everything.
6. **Bulk deactivation problems:**
   - A missing `actor` or a non-numeric id crashes.
   - Duplicate and unknown ids get audit entries for things that never happened.
   - The returned count includes users who were already inactive.
   - `actor` is whatever the caller sends, so it isn't a trustworthy identity.

**Should fix:** search ignores `per_page` and doesn't return the page fields, so it isn't paged the same way as the user list. The tests miss every issue above, and the case-insensitive search test would still pass if matching were case-sensitive.

**Minor:** an unused import, the README handler table isn't updated, and the page size is set in two places.

Fixes 1, 2 and 4 are only a few lines each, so a corrected version should be quick to re-review. I didn't change the code, and nothing was committed.