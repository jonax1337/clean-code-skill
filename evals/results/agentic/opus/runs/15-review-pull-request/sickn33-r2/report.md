I wrote the review to `REVIEW.md`. My recommendation is **don't merge it as it is**. All 28 tests pass, as the description says, but they don't cover the problems below. I ran each problem against the patched code to confirm it.

**Blocking:**
1. **SQL injection in search** (`adminhub/search.py:13`): the search term is pasted straight into the SQL. `q = "zzz' OR 1=1 OR '"` returned every user, and a name with an apostrophe (like O'Brien) crashes the handler.
2. **Audit failures are silently ignored** (`adminhub/audit.py:15-16`): the `except sqlite3.Error: pass` means the rollback in `deactivate_users` never runs. I removed the audit table and ran a bulk deactivation: the user was deactivated, the handler returned 200, and nothing was audited.
3. **Single-user deactivation still isn't audited** (`adminhub/users.py:47-52`), so "every deactivation in the audit trail" isn't true yet.
4. **`pages` is wrong** (`adminhub/api.py:37`): it rounds down. With 5 users and 10 per page it reports 0 pages. `per_page=0` crashes, and `per_page=-1` returns everyone with `pages: -5`. No test checks `pages`.

**Should fix:**
- Bad `page`, `ids` or `actor` values crash the handler instead of returning a 400.
- Bulk deactivation writes audit entries for ids that don't exist.
- The audit `actor` is taken from the request, so a caller can put any name there.
- Search ignores `per_page` and doesn't return `page`/`pages`, even though the description says it's paged like the user list.

**Minor:** an unused `import os`, the README wasn't updated, and a note on the case-insensitivity test.

Fixes 1–4 are each small and local, so the PR should be ready to approve soon after them. I tested in a temporary worktree and deleted it afterwards; the only change in the repo is the new `REVIEW.md`.