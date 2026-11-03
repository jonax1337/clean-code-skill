The email, name and role checks now live in one place, `src/userValidation.js`, and all three handlers use it. A fix to the email pattern, the name limit, a message or the role list now only has to be made there. All 29 tests pass with `npm test`.

**What's in the new file:** functions that clean up the email and name (trim them, and lowercase the email), one check per field that returns its error message or nothing, and the list of roles. The 80-character limit and the email pattern are also defined there, once each.

**What stays in each handler** is only what really differs between them:
- **`createUser`**: the role defaults to `member`.
- **`inviteUser`**: the name may be empty (only its length is checked), the role is required, and `owner` can't be invited. The allowed roles are taken from the shared list, so adding a role won't leave invitations behind.
- **`updateUser`**: it runs the same checks on just the fields that are present. The doc's "same rules as when creating" is now true by construction rather than by copying.

The error messages and their order (email, name, role) are unchanged.

**One behavior change: a bug fix.** `inviteUser` trimmed the email but didn't lowercase it, although `docs/api.md` says invitation emails are stored in lowercase. Because of that, inviting `Bob@x.com` and then `bob@x.com` created two pending invitations instead of answering 409. The shared email cleanup fixes this. Two new tests in `test/inviteUser.test.js` cover it; they failed before the change and pass now. Invitations already stored with capitals in the email aren't touched, which only matters if the real store keeps data between runs.

**Tests:** before refactoring, I added 13 tests across the three handler test files to pin the current behavior: the 80/81-character name limit, non-string and blank inputs, the order of messages, the `owner` role on invites, an empty invite name, and an update with no fields. Against the original code, 27 of 29 passed and only the two tests for the lowercase bug failed. After the refactor, all 29 pass.

I also added one line for the new file to the layout list in `README.md`. I didn't touch `listUsers`, `deleteUser` or the API doc. Nothing is committed yet.