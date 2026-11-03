The email, name and role checks now live in one new file, `src/validation.js`, and `createUser`, `updateUser` and `inviteUser` all call it. All 16 existing tests pass, and I didn't add tests for `validation.js` itself.

The file exports `validateEmail`, `validateName` and `validateRole`. Each returns either `{ value }` or `{ error }`. The role lists and the 80-character name limit are defined there too.

The handlers still differ where their rules differ, and I kept those differences as options:
- **Create:** `role` defaults to `member`.
- **Update:** only the fields present in the request are validated.
- **Invite:** a missing name is allowed, `role` is required, and only `admin`, `member` and `viewer` are accepted.

**Possible bug:** `inviteUser` trims the email but does not lowercase it, while the other two handlers do. The store compares emails case-sensitively. So inviting `ANN@example.com` doesn't hit the "email already in use" conflict when `ann@example.com` already exists. I kept that behavior and marked it with a comment, with `validateEmail(body.email, { lowercase: false })` at the call site. If you want it fixed, remove that option. That would change what invites accept, so I left the decision to you.