I've written the review to `REVIEW.md` in the repo root. I read `pr/482.diff` and `pr/482.md` but didn't apply the patch or run the tests, so I haven't confirmed the "28 passed" claim.

**I wouldn't merge it as it is.** The three main problems:

1. **SQL injection in search** (`adminhub/search.py:103-107`): the search term goes into the query through an f-string. It should use bound parameters, and `%` and `_` should be escaped.
2. **Audit failures are swallowed** (`adminhub/audit.py:66-67`): `record()` catches every `sqlite3.Error` and ignores it. Users can be deactivated with no audit row and no error, and the rollback in `deactivate_users` never triggers. Compliance is the reason for the audit log.
3. **Wrong page count** (`adminhub/api.py`, `list_users`): floor division drops the last partial page. With 5 users and `per_page=2` it reports 2 pages when there are 3. No test asserts `pages`.

`REVIEW.md` also lists, in order of importance:
- **Unvalidated input:** `page` and `per_page` (and `ids` in bulk deactivate) aren't validated. For example, `per_page=0` crashes and a negative `per_page` bypasses the cap of 100.
- **Bulk deactivation:**
  - `actor` comes from the request, so the audit trail can be forged.
  - Unknown, duplicate and already-inactive ids are all audited.
  - There's no cap on the number of ids.
- **Behaviour change:** `list_users` now returns only 25 users by default, which truncates the list for existing clients.
- **Search paging:** `search` doesn't accept `per_page` or return `page` and `pages`.
- **Test gaps and small cleanups:** for example, an unused `import os`.