I wrote the review to `REVIEW.md` in the repo root. My verdict is **do not merge as it is.**

The most serious problem is a SQL injection in `adminhub/search.py:13`. The search term is pasted into the query with an f-string, so a `q` containing a quote changes the SQL.

Other blocking findings:
- **Audit failures are swallowed** (`adminhub/audit.py:15-16`), so a deactivation can commit with no audit row, which breaks the compliance requirement.
- **Single-user deactivation is not audited** at all, although the PR description says every deactivation is.
- **`actor` comes from the request body**, so the audit trail can be forged.
- **Audit rows are written for ids that did not change** (unknown or already inactive).
- **Page count uses floor division**, so the last page is unreachable for counts that are not multiples of `per_page`.

The review also lists validation gaps (non-numeric input and `per_page=0` return 500s), a search pager that is not wired up, and tests that miss these paths.

What I checked:
- The patch applies cleanly to `main`.
- The README's "pages start at 1" claim matches the code.

What I did not check:
- I did not run the test suite. The patch is untrusted code, and I kept to reading it. The "28 passed" claim in the description is therefore unverified.