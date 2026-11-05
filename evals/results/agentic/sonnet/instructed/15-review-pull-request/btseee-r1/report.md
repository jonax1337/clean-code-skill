I've written the review to `REVIEW.md`. I would not merge PR 482 as it is.

I only read the diff and the description. I didn't apply the patch or run the tests, so I haven't confirmed the "28 passed" in the description.

Four findings block the merge:
1. **SQL injection:** `search.py:13` puts the search term straight into the SQL string. Use bound parameters.
2. **Lost audit entries:** `audit.py:15-16` catches every database error and ignores it. A failed audit write would still commit the deactivation, which breaks the compliance requirement.
3. **Wrong page count:** `list_users` computes `pages` by rounding down. With 5 users and 25 per page it returns 0 pages.
4. **Unchecked paging values:** `per_page=0` crashes with a division by zero, and `per_page=-1` returns the whole table, bypassing the 100-row cap. Bad `page` values and non-numbers aren't handled either.

Four more should be fixed in the same PR:
- **Audit actor:** it comes from the request body, so the audit trail can be forged.
- **`ids` input:** it isn't validated, and a string like `"123"` is treated as ids 1, 2 and 3.
- **Audit rows and count:** rows are written for ids that don't exist or are already inactive. The existing single-user `deactivate_user` writes no audit row at all.
- **Default list size:** the user list now silently returns only 25 users by default, which is a behaviour change for existing callers.

`REVIEW.md` also lists minor items (an unused import, a leftover TODO, an unstable sort order) and the test gaps. The fixes are small, so it could still go in today once they're done.