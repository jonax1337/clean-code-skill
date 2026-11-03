The email, name and role checks now live in one new file, `src/validation.js`. `createUser`, `updateUser` and `inviteUser` all call it, and all 16 existing tests still pass. I didn't add tests for the new module.

The file exports `validateEmail`, `validateName` and `validateRole`. Each returns `{ value }` or `{ message }`, and the message strings are unchanged because the API docs treat them as a contract.

The handlers keep the rules that are specific to them, passed in as options:
- **`createUser`:** the role defaults to `member`.
- **`inviteUser`:** the name is optional, the role is required, and `owner` is not allowed.
- **`updateUser`:** only the fields that are present are validated, and a body with none of them is rejected with `no fields to update`.

**Behaviour change in `inviteUser`:** it used to trim the email but not lowercase it. `docs/api.md` says emails are stored lowercase for invitations too, so I treated that as a bug. An invite for `Bob@Example.com` is now stored as `bob@example.com`. The duplicate check against users and pending invitations also uses the lowercased address, so it now catches case-variant duplicates it used to miss. No existing test covered this.