The email, name and role checks now live in one file, `src/validation.js`, and `createUser`, `updateUser` and `inviteUser` all use it. All 19 tests pass: the 16 existing ones unchanged, plus 3 new unit tests for the shared validators. The change is committed locally as `35feed5`, and I haven't pushed it.

Behavior is the same as before, including the differences between the handlers. These are now options on the shared validators:
- **Email:** `createUser` and `updateUser` lowercase it; `inviteUser` doesn't.
- **Name:** `inviteUser` allows an empty name.
- **Role:** `inviteUser` accepts only admin, member and viewer, and requires a role. `createUser` defaults to member.

I did not change one thing: `inviteUser` keeps the email's original case, while the other two lowercase it. So inviting `Bob@x.io` when `bob@x.io` already exists wouldn't be caught as a duplicate. That looks like a bug, but fixing it would change behavior, so I left it. With the shared validator it's a one-word change (add `{ lowercase: true }` in `inviteUser`). Do you want me to make it?

**Log**
- I read the three handlers and ran the tests for a green baseline.
- I wrote `test/validation.test.js` and `src/validation.js` with `validateEmail`, `validateName` and `validateRole`.
- I rewrote the three handlers to use them. `updateUser` now loops over a small field table instead of repeating the same block three times.
- I reran the tests and committed.

I skipped the crapper, dryer and mutator tools. I didn't find them in this environment.