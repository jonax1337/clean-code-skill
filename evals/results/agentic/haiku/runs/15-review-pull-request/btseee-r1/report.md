I wrote the review to `REVIEW.md` in the repo root. I would not merge PR 482 as it is.

The test suite passes (28 tests, as the PR says), but the tests don't cover the problems below. I applied the patch to a scratch copy, left your repo untouched, and ran targeted probes.

**Blocking:**
1. **SQL injection in search** (`adminhub/search.py:13`). The search term is interpolated into the SQL string, contrary to the README's "`?` placeholders" rule. `q = "' OR 1=1 OR '"` returns every user.
2. **Unaudited deactivations** (`adminhub/audit.py:15-16`). `audit.record` swallows `sqlite3.Error`, and the bulk deactivation commits anyway. With the `audit_log` table missing, the endpoint returns 200, deactivates the users, and writes no audit entry. The PR says compliance requires every deactivation to be audited.

**Also important:**
3. **Audit actor comes from the request body** (`adminhub/api.py:62`). A client can record any actor name. Please confirm the web layer sets it from the session. I couldn't find that layer in this repo.
4. **Audit entries don't match what changed** (`adminhub/users.py:61-63`). Unknown ids get audit rows, repeated ids get two rows, and already-inactive users are re-audited.
5. **Pager count is wrong** (`adminhub/api.py:37`). It uses floor division, so with 5 users at 2 per page it reports 2 pages, but page 3 holds user 5. `per_page=0` raises `ZeroDivisionError`.
6. **`page` and `per_page` aren't validated** (`adminhub/api.py:35-36`, `46`). Page 0 and negative values are accepted, `per_page=-5` returns all users, and `page=abc` raises an uncaught `ValueError`.

**Needs a decision:**
7. **Default page size changed** (`adminhub/api.py:34-39`). A call with no parameters now returns 25 users, not all of them. The README still says "all users", and the PR doesn't mention the change.

**Lower priority:** the bulk endpoint has no cap on the number of ids, the tests miss all of the cases above, and there are small cleanups (an unused `import os`, an open TODO, the README handler table).

The PR can merge once #1 to #6 are fixed and tested, and #7 is resolved. Your console team's timeline is a judgment call for you. If it matters more, the search handler could be split out of this PR and the rest fixed first.