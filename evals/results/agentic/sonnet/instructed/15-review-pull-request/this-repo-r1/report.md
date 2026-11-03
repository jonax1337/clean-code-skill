I wrote the review to `REVIEW.md`. **I wouldn't merge PR 482 as it is.** I read the diff and description only. I didn't apply the patch or run the tests, so the "28 passed" is unchecked.

Three problems must be fixed first:
1. **SQL injection in search:** `search.py:13` puts `q` straight into the SQL string. It should be a bound parameter.
2. **Audit failures are swallowed:** `audit.py:15-16` catches `sqlite3.Error` and does nothing. Deactivations could then be committed with no audit entry, which defeats the compliance requirement.
3. **Wrong page count:** `api.py:37` rounds the page count down. With 5 users and `per_page=3` it returns 1 page instead of 2, so the pager loses the last page.

Three more should go in the same PR:
- **Paging input isn't validated:**
  - `per_page=0` crashes with a divide by zero.
  - `per_page=-1` slips past the cap of 100 and returns the whole table.
  - `page=abc` raises a `ValueError`.
- **Bulk deactivation audits ids that weren't changed:** unknown, already-inactive and duplicate ids still get an audit entry. It also behaves differently from the single `deactivate_user`, which raises `NotFound`.
- **The audit actor comes from the request:** `params["actor"]` can be spoofed and raises `KeyError` if it's missing.

The review also lists smaller points and the tests that would catch each bug. Search doesn't return `page`/`pages` as the description says, bulk ids aren't capped, and there's an unused `import os`.

Fixing the six should be quick. The paging code, the single transaction and the small modules are fine.