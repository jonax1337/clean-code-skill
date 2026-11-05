The email, name and role checks now live in `src/validation/userFields.js`, and all three handlers use it. All 23 tests pass, including the 16 that existed before.

The module has one validator per field. Each returns either a cleaned value or the exact message from `docs/api.md`. A small `collectResults` helper gathers them and keeps the order email, name, role.

- **`createUser`** uses the full rules, with `member` as the default role.
- **`updateUser`** validates only the fields that are present, as before.
- **`inviteUser`** has two variants: an optional name that may be blank, and a role that is required and cannot be `owner`. Both are validators in the same module, so the rules sit next to the general ones.

I also added `test/userFields.test.js` and listed `src/validation/` in the README layout.

**Behaviour change:** `inviteUser` used to trim the email but not lowercase it. `docs/api.md` says invitation emails are stored in lowercase, and the store compares emails case-sensitively. So `Bob@Example.com` was stored as typed, and an invite for `ANN@example.com` would not have hit the 409 for an existing user. Sharing the email check fixes both, and I added a test for it. Existing invitation data is not migrated, so any mixed-case emails already stored stay as they are.

I haven't committed anything.