The email, name and role checks now live in one new file, `src/userValidation.js`. `createUser`, `updateUser` and `inviteUser` all call it. All 16 existing tests pass, and I didn't change the error messages or status codes.

**What's in the shared file**
- It has three validators: `validateEmail`, `validateName` and `validateRole`. The patterns, the role list and the 80-character limit are defined only there.
- The three handlers keep only what is specific to them: create defaults the role to `member`, update only checks fields that are present, and invite restricts the allowed roles and requires a role.

**Differences between the handlers**
- **Invitation emails:** `inviteUser` was trimming the email but not lowercasing it, while the other two lowercase. I kept that, using a `lowercase: false` option, so this change doesn't alter behavior.
- **Possible bug in that difference:** `Bob@X.com` can be invited even if `bob@x.com` is already a user, because the duplicate check compares exact strings. If that's unintended, delete the `{ lowercase: false }` argument in `inviteUser.js`.
- **Invite name:** the invitee's name stays optional through `required: false`.
- **Tests:** I didn't add tests for `userValidation.js` itself. The handler tests cover it indirectly.