# Review of PR 482 (user search, paged list, bulk deactivation)

Verdict: request changes. Do not merge as it is; the first finding is a security hole, the other two are bugs the
new tests do not catch.

## Must fix

1. **SQL injection in `search_users`** (`adminhub/search.py:13`). The search term comes straight from the `q`
   request parameter (`adminhub/api.py:43`, `search` handler) and is interpolated into the SQL with an f-string:
   `f"WHERE name LIKE '%{term}%' OR email LIKE '%{term}%' "`. Anyone who can call the console can inject SQL.
   `limit` and `offset` are already bound with `?`, so only the pattern is missing: build it in Python
   (`pattern = f"%{term}%"`) and pass it as a bound parameter, for example `WHERE name LIKE ? OR email LIKE ?`.
   The README says all queries use `?` placeholders; this one breaks that rule. Escaping `%` and `_` in the term is
   worth a thought as well.

2. **`pages` is wrong in the list handler** (`adminhub/api.py:37`). `total_pages = users.count_users(conn) // per_page`
   floors the division, so a partial last page is never counted: 5 users with `per_page=2` report 2 pages instead of
   3, and the default `per_page` of 25 with 5 users reports `pages: 0`. Use a ceiling division, for example
   `-(-total // per_page)`. The new tests only check the length of a page (`tests/test_users.py`,
   `tests/test_api.py`), never the `pages` value, so CI stays green. Add a test with a count that is not a multiple of
   `per_page`. Related: `per_page=0` raises `ZeroDivisionError` here.

3. **Swallowed exception in `audit.record`** (`adminhub/audit.py:15-16`). `except sqlite3.Error: pass` throws away
   every database error while writing the audit entry. The PR description says the audit trail is a compliance
   requirement, yet `deactivate_users` would happily deactivate users and commit with no audit rows when the insert
   fails (locked database, missing table, full disk), and nobody would notice. Let the error propagate. The caller in
   `adminhub/users.py:62-63` already rolls back and re-raises, so the whole bulk deactivation fails loudly, which is
   what you want here.

## Checked and fine

- `deactivate_users` (`adminhub/users.py:59-61`) builds the `IN (...)` list with an f-string, which looks like SQL
   interpolation, but the f-string only contains generated `?` markers; the ids are passed as bound parameters. No
   injection risk. The `except Exception` at line 65 rolls back and re-raises, so nothing is swallowed.
- `search_users` pages with `(page - 1) * per_page`, consistent with "pages start at 1".

## Nits

- `adminhub/search.py:3`: `import os` is unused.
- `adminhub/search.py:10`: TODO comment; track it in the issue tracker instead.
- `adminhub/search.py:9`: `per_page=25` duplicates `users.DEFAULT_PAGE_SIZE`; the `100` cap in `api.py:36` is a magic
  number too.
- `adminhub/search.py:16`: `res` is a vague name, and `search_users` has no docstring while its neighbours do.
