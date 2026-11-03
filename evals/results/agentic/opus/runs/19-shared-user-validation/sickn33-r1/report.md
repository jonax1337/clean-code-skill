The email, name and role rules now live in one module, `src/userValidation.js`, and all three handlers use it. All 26 tests pass.

**How it fits together**
- The module has `checkEmail`, `checkName` and `checkRole`, plus `ROLES` and `INVITABLE_ROLES`. The email pattern, the 80-character name limit and the message strings are each defined only here.
- `collectChecks` combines the three results into `{ values, messages }` and keeps the messages in the documented order: email, name, role.
- Each handler now only says what's different about it:
  - **create:** role defaults to `member` when it's missing.
  - **update:** only the fields that are present get checked.
  - **invite:** name is optional (`checkName(..., { optional: true })`), and the allowed roles are `INVITABLE_ROLES`, which leaves out `owner`.
- All error messages are word-for-word the same as before, since `docs/api.md` says clients match on them.

**One behavior change:** `inviteUser` used to trim the email but didn't lowercase it, so `Ann@example.com` was saved as typed. That also meant it wasn't caught as a duplicate of an existing `ann@example.com`. `docs/api.md` says invitation emails are stored in lowercase, so this was one of the out-of-sync copy bugs you mentioned. With a single email check it's fixed automatically. If you'd rather keep the old behavior for now, that would mean adding the inconsistency back on purpose, so tell me.

**Tests**
- `test/userValidation.test.js` covers each rule directly, including blank and non-string input, the 80/81-character boundary, optional names, `owner` being rejected for invites, and message order.
- I added a regression test for the invite lowercase fix. It fails against the old code and passes now, and it's the only test that changed result. I also added tests that inviting `owner` is rejected and that an update body with no known fields is rejected.

Nothing is committed yet.