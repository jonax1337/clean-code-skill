The email, name and role checks now live in one file, `src/userFields.js`, and `createUser`, `updateUser` and `inviteUser` all call it instead of carrying their own copies. All 23 tests pass. Nothing is committed.

**How it works**
- **The shared checks:** `checkEmail`, `checkName`, `checkOptionalName` and `checkRole(input, allowedRoles)`. Each one returns either the cleaned-up value or the exact error message from `docs/api.md`. The email pattern, the 80-character name limit and the role lists (`ROLES`, plus `INVITABLE_ROLES`, which leaves out `owner`) are also defined only here.
- **`collectChecks`:** combines the results into the valid values and the messages, in the order email, name, role.
- **What stays in each handler:** only the rules that really differ between them:
  - **create:** the role defaults to `member`.
  - **update:** only fields present in the request are checked, and an empty request gets `no fields to update`.
  - **invite:** the name is optional, the role is required, and `owner` can't be granted.

**One behavior change: invitation emails are now lowercased.** The old `inviteUser` trimmed the email but didn't lowercase it, which goes against `docs/api.md`. Two problems came from that: invitations were stored with mixed-case emails, and inviting `ANN@example.com` didn't get a 409 even though `ann@example.com` was already a user. The shared email check fixes both. I added tests for these, and confirmed they fail on the old code and pass now. If any invitations are already stored with mixed-case emails, this change doesn't convert them.

**Other new tests** cover rules that are easy to break during a refactor like this:
- the order of error messages when several fields fail
- a blank name in an update
- an update with no fields
- a blank name in an invitation being stored as `''`
- `owner` being rejected for invitations

Error messages and responses are otherwise unchanged.