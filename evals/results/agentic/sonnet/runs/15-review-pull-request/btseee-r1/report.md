I've written the review to `REVIEW.md`. My verdict is not to merge PR 482 as it is.

I applied the patch to a clean copy and ran the tests: 28 passed, as the PR says. I also ran a few small checks against the patched code, and those back up the points below.

**Blocks the merge:**
- **SQL injection in search:** `search_users` puts the `q` parameter straight into the SQL text, which breaks the README's rule that all queries use `?` placeholders. The `%` and `_` wildcards in `q` also aren't escaped; searching for `%` returned every user.
- **Audit entries can be lost silently:** `audit.record` swallows database errors, so a deactivation can commit with no audit entry. When I dropped the `audit_log` table, bulk deactivation still deactivated both users and raised no error. Compliance asked for every deactivation to be audited.

**Fix before merging:**
- **Audit log can be spoofed or padded:**
  - The actor comes from the request parameters, so the caller can write any name into the log.
  - Every id in the list is audited, including ids that don't exist.
  - The existing single-user deactivation still writes no audit entry.
- **Wrong page count:** `pages` is rounded down, so 5 users at 3 per page reports 1 page instead of 2. The pager the console team is waiting for would hide the last page.
- **Unchecked paging parameters:**
  - `per_page=0` crashes.
  - A negative `per_page` returns every row.
  - Non-numeric values give a 500 instead of a 400.
- **Behavior change:** `list_users` now returns 25 users by default instead of all of them, and the README doesn't say so.

`REVIEW.md` also lists lower-priority items, open questions and the missing tests. The paged list could ship on its own once the page-count and paging-parameter issues are fixed, since it doesn't depend on the search or audit code.