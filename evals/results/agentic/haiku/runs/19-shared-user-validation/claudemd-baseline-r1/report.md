The three handlers now share one set of user validation rules in `src/validation/user.js`. All 25 tests pass: the 16 existing ones and 9 new ones for the shared rules.

- **Shared module:** `checkEmail`, `checkName` and `checkRole` each push at most one message and return the cleaned value, or `undefined` when rejected. The role lists and the 80-character limit live there too.
- **Handlers:** `createUser`, `updateUser` and `inviteUser` now call those checks and keep only their own logic (defaults, partial updates, duplicate-email conflicts). Message order and wording are unchanged, so `docs/api.md` still holds.
- **Per-handler differences:** these are passed as options rather than hidden in the shared code. Invitations skip lowercasing, the name is optional, the role is required, and `owner` is excluded.
- **Tests:** `test/validation.test.js` covers each rule directly.

I did not commit anything.

**Existing bug, left unfixed:** `docs/api.md` says emails are stored lowercase for users and invitations alike, but `inviteUser` never lowercases. An invite for `Bob@Example.com` is stored as typed, and the duplicate check against a lowercase user email will miss it. I kept that behavior because fixing it changes what gets stored. Lowercasing invitation emails and adding a test for it is a one-line change in `inviteUser.js`, plus removing the `lowercase: false` option. Say if you want that done.