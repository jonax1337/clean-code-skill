**Do not merge PR 482 as it is.** The review is in `REVIEW.md` at the repo root.

The suite passes (28 tests), but the patch has a SQL injection and several audit and paging defects. I applied the patch to a scratch copy of `main` and confirmed each finding with probe scripts. The working tree only has `REVIEW.md` added, and nothing is committed.

Most important findings (file and line in the patched code):

1. **SQL injection in `search`** (`adminhub/search.py:13`). The `q` value is put into the query with an f-string. A crafted `q` returned all 3 test users, while a normal non-matching term returned none. This blocks the merge on its own, and it contradicts the README's "all queries use `?` placeholders" rule.
2. **Audit entries for users that were never deactivated** (`adminhub/users.py:61-63`). Bulk deactivation audits every submitted id. With ids `2` and `99`, the audit log got rows for both, but only one user changed.
3. **Audit failures are silently swallowed** (`adminhub/audit.py:15-16`). With the audit table missing, the deactivation committed with no audit row and no error.
4. **Single-user deactivation is not audited** (`adminhub/api.py:50-57`). The PR says every deactivation is audited, so this misses the compliance requirement.
5. **Wrong page count** (`adminhub/api.py:37`). Floor division gives `pages: 2` for 5 users at 2 per page; the correct value is 3, so the console's pager cannot reach the last page. The tests check only the length of the user list, so they miss this.
6. **Audit actor comes from the request body** (`adminhub/api.py:62`). A caller can record any name in the audit log.
7. **Bad input gives exceptions instead of 400s**, for example `per_page=0` (divide by zero), `page=abc`, and bulk deactivation without `actor`.

The review also covers medium and low items: test gaps, an unused import, and a README that was not updated.

The pager and bulk deactivation can ship once findings 1–5 are fixed. Search can follow separately if it cannot be fixed today.