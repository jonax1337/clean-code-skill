I wrote the review to `REVIEW.md` in the repo root. My verdict is **do not merge as it is**.

The patch applies cleanly and the suite passes (28 tests), as the PR says. Probing the new code showed two blockers and several correctness problems.

**Blockers**
1. **SQL injection in `search_users`** (`adminhub/search.py:13`). The search term is interpolated into the query with an f-string. A crafted `q` (`zzz%' OR 1=1 OR '`) returned all 5 users. This also contradicts the README's rule that all queries use `?` placeholders.
2. **Audit failures are silently swallowed** (`adminhub/audit.py:15-16`). With the `audit_log` table dropped, bulk deactivation returned 200 and deactivated the user with no audit row. Compliance will rely on this trail.

**Should fix in this PR**
3. Bulk deactivation audits ids that did not change anything: a nonexistent id gets an audit row, duplicate ids get two rows, and an already-inactive user is counted as deactivated.
4. The page count rounds down (`api.py:37`). With 5 users at `per_page=2` it reports 2 pages, so the last page is unreachable.
5. Paging and id input are not validated. `per_page=0` raises `ZeroDivisionError`, `page=-1` returns 200, and bad integers raise bare `ValueError` instead of a 400.
6. The audit `actor` comes from caller-supplied params, so it can be forged, and a missing actor gives a `KeyError`.

The review also covers the minor items: `search` has no pager fields, the README is stale, there is an unused import, and the tests miss these cases. I could not verify that the new handlers are routed, because the web layer is not in this repo.

I did not commit anything, and the scratch copy is in a temp directory. The console team's deadline is real, but I would not merge a search endpoint with a known injection until finding 1 is fixed and tested.