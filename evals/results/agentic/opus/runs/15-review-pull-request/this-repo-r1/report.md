I've written the review to `REVIEW.md`. My recommendation is **don't merge PR 482 as it is.** The tests pass (I applied the patch to a temporary copy, ran `pytest`, and got 28 passed), but trying the new handlers by hand turned up real problems:

1. **SQL injection in search** (`adminhub/search.py:13`). The search term goes straight into the query text. A crafted `q` returns every user, and an ordinary name like `O'Brien` causes a server error.
2. **Audit failures are silently ignored** (`adminhub/audit.py:15-16`). If writing an audit entry fails, the error is swallowed, the users are still deactivated and saved, and the request reports success. I made this happen. That defeats the compliance requirement the PR was written for.
3. **The page count is wrong** (`adminhub/api.py:37`). It rounds down, so with 5 users and 3 per page it reports 1 page instead of 2. With the default page size and fewer than 25 users it reports 0 pages.
4. **Bad paging input crashes the handler.** `per_page=0` and `page=x` cause server errors instead of a 400 response. `per_page=-1` gets around the 100-per-page limit.
5. **Bulk deactivation has two problems.** A missing `actor` crashes it, and it writes audit entries for ids that don't exist.

There is also one open question you need to answer: where does `actor` come from? If the client sends it in the request, anyone can put any name in the audit log.

The review also covers some smaller issues:
- `list_users` now returns only 25 users by default instead of all of them, and the README wasn't updated.
- `search` doesn't page the way the PR description says it does.
- There's an unused import and a leftover TODO.

Each item lists the tests that would catch it. The fixes are small, so a same-day merge is still realistic once they're done.