The user validation now lives in one module, `src/validation/user.js`, and the three handlers call it. All 17 tests pass: the original 16 plus one new test.

**What changed**
- `src/validation/user.js` holds the email pattern, the role lists, the name length limit, and the normalizers. Each check returns an error message or `null`.
- `createUser`, `updateUser` and `inviteUser` now compose those checks. Their status codes, conflict logic and per-handler differences (default role, optional invite name, invite-only roles, update-only-present-fields) are unchanged.
- The error messages are the same strings as before. I checked the output for the invalid cases.

**One behavior change to review**
- `inviteUser` used to skip the lowercase step on email. An invite for `Ann@example.com` could therefore slip past the duplicate check when `ann@example.com` already existed. It now lowercases like the other two handlers, and I added a test for that case. If you want the old behavior, it's a one-line change in `inviteUser.js`.

Nothing is committed.