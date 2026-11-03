I've written the review to `REVIEW.md`. I wouldn't merge PR 482 as it is.

I applied the patch to a temporary copy of the repo and ran the tests: 28 passed, as the PR says. I then called the handlers directly to confirm each problem below. The four blocking ones:

1. **SQL injection in search** (`adminhub/search.py:13`): `q` is pasted straight into the SQL. Searching for `zzz' OR 1=1 OR name LIKE '` returns all users, and an ordinary name like `O'Brien` causes a 500 error.
2. **Audit entries can be lost without an error** (`adminhub/audit.py:9-16`): `record()` ignores database errors. I deleted the `audit_log` table, and bulk deactivation still deactivated the user and returned 200, with nothing logged.
3. **The audit actor comes from the request** (`adminhub/api.py:59`): whoever calls the endpoint decides which name goes into the audit log.
4. **`pages` is wrong** (`adminhub/api.py:37`): the count is rounded down, so 5 users at 3 per page shows 1 page instead of 2, and at 10 per page it shows 0. No test checks `pages`.

It should also fix these:
- **Paging input isn't checked:** `per_page=0` crashes with a 500, `per_page=-1` returns every user and gets around the 100 cap, and non-numeric values cause 500s instead of 400s.
- **Bulk deactivation logs things that didn't happen:** it writes audit rows for unknown IDs and for users who were already inactive.
- **A string `ids` is read character by character:** `"45"` deactivated users 4 and 5.
- **Search doesn't page "the same way" as the PR says:** it ignores `per_page` and doesn't return `page`/`pages`.

The review also lists some minor points. All the fixes are small, so a same-day merge still looks realistic, but where the actor's name should come from probably needs a short conversation with the author first.