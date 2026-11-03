The user validation now lives in one module, `src/userValidation.js`. The email format, name length and role list are each defined once. The three handlers call it, and their behavior is unchanged. The tests pass: 20 of 20, up from 16, with 4 new tests for the shared rules.

**What changed**
- `src/userValidation.js` (new): `emailError`, `nameError`, `nameLengthError`, `roleError`, `trimmed`, plus the `ROLES`, `INVITABLE_ROLES` and length constants.
- `createUser.js`, `updateUser.js`, `inviteUser.js`: each keeps its own policy (required or optional, default role, which roles are allowed) and calls the shared checks. Messages and error order are the same.
- `test/userValidation.test.js` (new): tests for each shared rule.

**Verification**
- `npm test`: 20 pass, 0 fail.
- I compared the original handlers (from `HEAD`) with the new ones on 17,496 input combinations (emails, names, roles, ids, with and without a body). Status codes and response bodies matched every time. I deleted the scratch script afterwards.

**Decision for you: the three handlers were not identical**
- `inviteUser` does not lowercase the email, but `createUser` and `updateUser` do. That looks like a bug. An invitation for `Bob@Example.com` is stored as typed, so a later `createUser` with `bob@example.com` won't see it as a conflict. I kept the current behavior so this refactor changes nothing. If you want invitations lowercased too, it's a one-line change in `inviteUser.js`, but it changes stored data, so I didn't make it.
- The rule "name is optional when inviting" is kept in `inviteUser.js` on purpose. It is a policy, not a validation rule.

I haven't committed anything. The changes are in the working tree for you to review.