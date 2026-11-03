I moved the email, name and role checks into a new `src/validation.js`, and all three handlers now use it. `node --test` passes (17 tests). That count includes `test/helpers.js`, which node runs as a test file. I haven't committed anything.

- **Shared validators:** `validateEmail`, `validateName`, `validateOptionalName` and `validateRole` each return either `{ value }` or `{ error }`. The error message wording is unchanged, since the API docs say clients match on it. `collect()` gathers the values and the messages in field order (email, name, role).
- **`createUser`:** the role defaults to `member`.
- **`inviteUser`:** the name may be blank, and the role is required and limited to `admin`, `member` or `viewer`.
- **`updateUser`:** only the fields that are present are validated, and `no fields to update` is unchanged.

**One behaviour change in `inviteUser`:**
- **Before:** it trimmed the email but didn't lowercase it. `Bob@Example.com` was stored as typed, and the duplicate check against existing users and invitations was case-sensitive.
- **Now:** it lowercases like the other two handlers. `docs/api.md` says invitation emails are stored trimmed and in lowercase, so I treated the old behaviour as a bug.
- **Test:** I added one in `test/inviteUser.test.js` for this. If you'd rather keep the old behaviour, tell me and I'll make it an option.

I left the uniqueness checks (`findUserByEmail`, `findInvitationByEmail`) in the handlers, because they differ per handler and aren't validation.

I didn't add direct tests for `validation.js`. The existing handler tests cover it only partly, so it has no boundary tests yet, for example for the 80-character name limit or for `updateUser` with a blank name. I can add those next if you want.