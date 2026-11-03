I've written the review to `REVIEW.md`. My verdict is that I wouldn't merge PR 482 as it is. I read the diff and description only. I didn't apply the patch or run the tests, so I haven't confirmed the "28 passed" claim.

The five blockers, most important first:
1. **SQL injection** in `search.py:105`: the search term goes into the query through an f-string. It should use bound parameters.
2. **Audit failures are swallowed** in `audit.py:66-67`: a failed audit insert is ignored, so a deactivation can commit with no audit row.
3. **Wrong page count** in `api.py:20`: `count // per_page` rounds down. With 5 users and `per_page=3` it returns 1 page instead of 2, which will break the pager the console team is waiting for.
4. **Missing input validation** on `page` and `per_page`:
   - `per_page=0` crashes.
   - A negative `per_page` bypasses the 100 cap.
   - Non-numeric values give a 500 instead of a 400.
5. **Bulk deactivation:**
   - The actor comes from the request, so anyone can claim to be someone else.
   - Unknown, duplicate and already-inactive ids are audited anyway.
   - There is no limit on the number of ids.

Smaller points are in the file. The single-user `deactivate_user` isn't audited, `list_users` now truncates to 25 users by default without the README being updated, `search` returns no `pages`, and the tests only cover the happy paths.

Items 1 to 5 are small fixes, so a re-review after them should be quick.