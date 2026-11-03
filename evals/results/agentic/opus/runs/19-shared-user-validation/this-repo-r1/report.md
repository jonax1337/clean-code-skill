The email, name and role checks now live in one new file, `src/userValidation.js`. `createUser`, `updateUser` and `inviteUser` all call it, so a fix to a rule only has to be made there.

**How it works**
- There is one check per field: `checkEmail`, `checkName`, `checkOptionalName` and `checkRole(input, allowedRoles)`. Each returns either the cleaned-up value or the error message.
- The email pattern, the 80-character name limit, `ROLES` and `INVITABLE_ROLES` are each defined once. `INVITABLE_ROLES` is built from `ROLES` minus `owner`, so a new role only needs adding in one spot.
- The handlers keep only what is really theirs:
  - `createUser`: the role defaults to `member`.
  - `inviteUser`: the name is optional, the role is required, and `owner` can't be invited.
  - `updateUser`: only the fields that are sent get checked.
- The error messages are worded exactly as before (the API docs say clients rely on that wording), and errors still come back in the order email, name, role.

**One behavior change: an existing bug is fixed.** `inviteUser` was the copy that had drifted. It trimmed the email but didn't lowercase it, even though `docs/api.md` says invitation emails are stored in lowercase. Because of that, inviting `ANN@example.com` went through even when user `ann@example.com` already existed, and the invitation was saved with the capital letters. With the shared check, it now gets a `409`. A new test shows this: it failed on the old code and passes now.

**Tests**
- Before changing anything, I added 11 handler tests to lock in the current behavior: error order, the 80/81-character limit, `role: null`, `no fields to update`, an optional invite name, `owner` invites, and duplicate pending invitations. Run against the original code, 26 of 27 passed; the only failure was the lowercase bug above.
- After the refactor, `npm test` gives 27 tests, 27 passed.

There's no lint or type-check setup in the project, so nothing ran beyond the tests. I didn't touch `listUsers` or `deleteUser`, and nothing is committed yet.