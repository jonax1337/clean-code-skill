The email, name and role checks now live in one module, `src/validation/userFields.js`. `createUser`, `updateUser` and `inviteUser` all call it. All 21 tests pass: the 16 existing ones plus 5 new unit tests for the shared rules. I didn't commit anything.

**What changed**
- **`src/validation/userFields.js`** (new): `validateEmail`, `validateName` and `validateRole`, plus the shared constants (`EMAIL_PATTERN`, `ROLES`, `INVITABLE_ROLES`, `DEFAULT_ROLE`, `MAX_NAME_LENGTH`). Each returns `{ value, error }`.
- **The three handlers** keep their own policy as options, so a fix to a rule now happens in one place.
- **`test/userFields.test.js`** (new): covers the shared rules directly.

**Behavior I kept on purpose**
- Create and update lowercase the email. Invite only trims it (`lowercase: false`).
- Name is required for create and update, optional for invite.
- Create defaults a missing role to `member`. Update validates the role only when it is present. Invite requires a role and accepts only `admin`, `member` or `viewer`.
- Error messages and their order are unchanged.

**Worth a look:** the invite casing difference looks like a possible bug. An invitation stores the address as typed, so `Bob@Example.com` and `bob@example.com` can both be invited. The duplicate check (`findUserByEmail`) may not catch that. I didn't change it because it alters stored data. If you want invites lowercased, it's a one-line change in `inviteUser.js`.