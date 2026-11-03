I wrote the review to `REVIEW.md` in the repo root. I read the patch but didn't run the tests. My verdict is **do not merge as it is**.

The findings, most important first:

1. **SQL injection in `search_users`** (`adminhub/search.py`, diff line 105). The search term goes into the SQL through an f-string. It needs a bound parameter, and `%` and `_` should be escaped.
2. **`audit.record` swallows all database errors** (`adminhub/audit.py`, diff lines 66-67). A bulk deactivation can commit with no audit rows, which breaks the compliance requirement and the rollback in `deactivate_users`.
3. **Wrong page count** (`adminhub/api.py`, diff line 20). `total // per_page` rounds down, so the last partial page isn't counted and fewer users than `per_page` gives `pages: 0`. No test checks `page` or `pages`.
4. **Paging input isn't validated** (`adminhub/api.py`, diff lines 18-19 and 29). `per_page=0` crashes with a division by zero, and a negative `per_page` returns every row. `page=0` or a negative page silently returns the first page, and non-numeric values give a 500.
5. **`actor` comes from the request body** (`adminhub/api.py`, diff line 40). Callers can forge who did the deactivation, and a missing `actor` is a 500.

The remaining findings, in `REVIEW.md`:
- Bulk deactivation audits ids that weren't actually deactivated, unlike the single-user version, which raises `NotFound`.
- `search` ignores `per_page` and returns no `page` or `pages`, so the pager can't work for search results.
- There is an unused `import os` and a leftover TODO in `search.py`.
- Test gaps: injection, bad paging input, unknown ids in bulk, and the audit rows through the API.

Findings 1 to 3 are small fixes.

I didn't commit `REVIEW.md`.