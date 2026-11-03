The email, name and role checks now live in one file, `src/validation/user.js`. All three handlers use it, so a fix to a rule only has to be made there. All 21 tests pass: the 16 existing ones plus 5 new ones.

**How it works**
- `validateEmail`, `validateName` and `validateRole` each check one field and return either the cleaned value or the error message. The message text is unchanged, since `docs/api.md` says clients depend on it.
- `collect` runs the checks in order and gathers the values and messages, so errors still come out in the documented order: email, name, role.
- The real differences between the endpoints are now options instead of separate copies:
  - **`createUser`**: role defaults to `member`.
  - **`updateUser`**: only checks the fields that are present.
  - **`inviteUser`**: name may be empty (`optional: true`), role is required, and only `INVITABLE_ROLES` are allowed (every role except `owner`).
- I also added the new file to the layout list in the README.

**One behaviour change you should know about.** `inviteUser` trimmed the email but didn't lowercase it, unlike the other two handlers. That broke the rule in `docs/api.md` that invitation emails are stored in lowercase and matched case-insensitively. With the shared check:
- `Bob@Example.com` is now stored as `bob@example.com`.
- Inviting `ANN@example.com` when `ann@example.com` is already a user now returns `409` as it should. Before, it created a second invitation for the same address.

This is the kind of bug the shared code is meant to stop, and the new tests cover it. But it does change what the endpoint returns. If any invitations are stored outside this in-memory store, existing ones with mixed-case emails might need normalising.

Nothing is committed yet. Let me know if you want me to commit it.