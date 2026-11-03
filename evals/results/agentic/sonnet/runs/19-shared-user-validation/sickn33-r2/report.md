The email, name and role checks now live in one new file, `src/userValidation.js`. `createUser`, `updateUser` and `inviteUser` all call it, and all 16 existing tests pass. I didn't add new tests for the validators.

- **Validators:** `validateEmail`, `validateName` and `validateRole` each return either `{ value }` or `{ error }`. The error messages are the same as before.
- **`createUser`:** it runs the three validators and collects their errors.
- **`updateUser`:** it runs each validator only for fields that are present in the request body. Adding a field later means adding one entry to the `FIELD_VALIDATORS` map in `src/handlers/updateUser.js`.
- **`inviteUser`:** the places where it differs from the others are now explicit options:
  - `lowercase: false` for the email.
  - `required: false` for the name.
  - Its own `INVITABLE_ROLES` list, which leaves out `owner`.
  - The "role is required" check stays in the handler.

I kept every difference between the three handlers as it was. One of them looks odd to me: `inviteUser` doesn't lowercase the email, but `createUser` and `updateUser` do. If `findUserByEmail` compares case-sensitively, inviting `Bob@x.com` wouldn't detect an existing user stored as `bob@x.com`. If that isn't deliberate, it's a one-word fix: drop `{ lowercase: false }` in `inviteUser`.