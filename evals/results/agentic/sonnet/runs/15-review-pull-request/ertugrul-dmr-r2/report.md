I wrote the review to `REVIEW.md`. I wouldn't merge PR 482 as it is.

I applied the patch to a clean copy of `main`, and the 28 tests pass, as the description says. The tests don't cover the problems below. I reproduced every blocking item except the audit-log one (item 2).

Blocking:
1. **SQL injection in search** (`adminhub/search.py:13`): the search term is pasted into the SQL. A `q` of `' OR '1'='1` returned all 5 users.
2. **Audit failures are swallowed** (`adminhub/audit.py:15-16`): a failed audit insert is ignored. The deactivations still commit, so the compliance trail can silently lose entries.
3. **Wrong page count** (`adminhub/api.py:37`): it rounds down. With 5 users and `per_page=3` it returns 1 page instead of 2, and with the default page size it returns 0 instead of 1.
4. **Paging parameters aren't validated:**
   - `per_page=0` crashes with `ZeroDivisionError`.
   - `per_page=-1` bypasses the cap of 100 and returns every user.
   - `page=0` gives a negative offset.
   - Non-numeric input causes a 500 instead of a 400.

Should fix: audit rows are written for ids that don't exist, `actor` is taken from the request body, and the number of ids per request isn't limited. There are also a few minor cleanups, such as an unused `os` import and a TODO left in the code. `REVIEW.md` has the file and line for each.

The fixes are small, so it could still go in today once items 1 to 4 are done. I'd also fix item 5 first, because the audit log is meant for compliance.