The email, name and role checks now live in one place, `src/userValidation.js`, and all three handlers use it. A future fix only needs to be made there.

**How it works**
- There are three functions: `validateEmail`, `validateName` and `validateRole`. Each returns either the cleaned-up value or the error message clients already receive. I kept the message wording exactly as before, since `docs/api.md` says clients depend on it.
- Where the endpoints genuinely differ, the difference is now an explicit option instead of a separate copy:
  - Invites call `validateName(..., { required: false })`, because the name is optional there.
  - Invites call `validateRole(..., { allowed: INVITABLE_ROLES })`, so `owner` can't be granted by invitation.
  - Create still defaults the role to `member`, and update still only checks fields that are present. Both are handled in the handler before calling the shared check.
- Error messages still come out in the order email, name, role.

**One behaviour change: an existing bug got fixed**
`inviteUser` trimmed emails but never lowercased them, even though `docs/api.md` says invitation emails are stored in lowercase. In practice:
- An invite to `ANN@example.com` went through even when `ann@example.com` was already a user.
- The invitation was stored with its original capitals.

The shared check always lowercases, so that's fixed now. I added a regression test for it and confirmed it fails against the old `inviteUser` code. Any invitations already stored with capitals will stay that way; this change doesn't touch existing data.

**Tests**
- New `test/userValidation.test.js` with unit tests for each check, including the 80-character name limit and the allowed-roles list.
- Two new tests in `test/inviteUser.test.js`: the lowercase regression test, and one confirming the `owner` role is rejected.
- `npm test` passes: 23 tests, 0 failures (16 before this change).

I haven't committed anything.