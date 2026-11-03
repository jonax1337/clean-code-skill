The user-field checks now live in one module, `src/validation/userFields.js`. `createUser`, `updateUser` and `inviteUser` import from it, so an email, name or role rule only needs fixing there. All 16 existing tests pass, the same as before the change. I did not commit.

The module exports:
- **Shared rules:** `emailErrors`, `nameErrors` and `roleErrors`, which return the same messages as before.
- **Normalizers:** `normalizeEmail` and `normalizeName`.
- **Role lists and length limit:** `ALL_ROLES`, `INVITABLE_ROLES` and `MAX_NAME_LENGTH`.

Each handler still decides which fields are required and which roles it accepts. Create defaults the role to `member`. Invite allows an empty name, requires a role and only accepts invitable roles. Update only checks the fields that were sent. I kept these differences because they look intentional.

**One inconsistency I preserved:** `inviteUser` trims the email but does not lowercase it, while create and update do lowercase it. That means `Ann@Example.com` can be stored as typed when invited, and the duplicate check may miss a case-different match. This could be a bug. Changing it would alter invite behavior, so I left it alone. If you want it fixed, the change is one line: remove the `{ lowercase: false }` argument in `src/handlers/inviteUser.js`.