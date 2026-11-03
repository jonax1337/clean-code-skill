I moved the email, name and role checks into one new module, `src/validation.js`, and `createUser`, `updateUser` and `inviteUser` now all call it. All 16 tests pass. Nothing is committed.

The module has `validateEmail`, `validateName` and `validateRole`. The email pattern, the 80-character name limit and the role lists are now defined once.

I kept each handler's existing behavior, so the places where they differ are options on the shared functions rather than separate copies:
- **Email case:** `inviteUser` doesn't lowercase emails, while the other two do. This is `validateEmail(x, { lowercase: false })`.
- **Name:** `inviteUser` allows an empty name. This is `validateName(x, { required: false })`.
- **Role:** `inviteUser` only accepts `admin`, `member` or `viewer`, and it requires a role, while `createUser` defaults to `member`. This is `validateRole(x, { allowed: INVITABLE_ROLES })`.
- **`updateUser`:** it loops over the three fields and validates only the ones present in the request.

The invite flow keeps emails as typed, so `Bob@X.com` and `bob@x.com` are treated as different when checking for duplicates. That looks accidental to me, but changing it would alter behavior, so I left it. If you want it fixed, it's one line: drop the `lowercase: false` in `inviteUser`.