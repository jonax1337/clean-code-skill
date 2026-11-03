The email, name and role rules now live in one place, `src/validation/user.js`. All three handlers call it. All 24 tests pass: the 16 existing ones and 8 new ones.

**How it works**
- `validateUser(body, options)` checks and cleans up email, name and role. It returns `{ values, messages }`, with messages in the documented order (email, name, role) and the exact wording from `docs/api.md`.
- Each handler's differences are now options instead of separate copies of the code:
  - **`createUser`**: `{ defaultRole: 'member' }`
  - **`updateUser`**: `{ partial: true }`, so it only checks fields that are present, using the same rules as create
  - **`inviteUser`**: `{ nameOptional: true, roles: INVITABLE_ROLES }`. The name can be missing or blank, and `owner` can't be granted.
- The email pattern, the 80-character name limit and the role lists are defined once in that module. Each handler now only does its own work: the 404 lookup, the "no fields to update" check, conflict checks and saving.

**One behaviour change:** `inviteUser` trimmed the email but never lowercased it. The docs say invitation emails are stored in lowercase, so `Bob@Example.COM` was saved as typed. It also didn't count as a duplicate of an existing user `ann@example.com` if it was typed as `ANN@example.com`. Since all three now share one validator, invitations get lowercased like the others. I added a test that would have failed on the old code. If any existing invitation data was saved in mixed case, it won't match the new lowercased lookups, so it may be worth checking.

**New tests**
- `test/validation.user.test.js` tests the shared rules directly: message order, blank and non-string input, partial mode, optional name, and a required role.
- `test/inviteUser.test.js` has two new cases: the lowercase/case-insensitive duplicate check, and rejecting `owner`.

I haven't committed anything. Let me know if you'd like a branch and commit.