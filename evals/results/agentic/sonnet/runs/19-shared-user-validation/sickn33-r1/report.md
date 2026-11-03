I moved the email, name and role checks into one new module, `src/userValidation.js`. `createUser`, `updateUser` and `inviteUser` now call it instead of carrying their own copies. All 16 existing tests pass. I didn't add tests for the new module.

- **Shared checks:** The module has `validateEmail`, `validateName` and `validateRole`. It also holds the email pattern, the 80-character name limit and the role lists, plus a small `collectResults` helper that gathers error messages and cleaned values. A fix to one of these rules is now made once.
- **Behavior is unchanged:** The three handlers differ in a few ways, and I kept each difference as an option rather than merging them:
  - `inviteUser` makes the name optional (`required: false`).
  - `inviteUser` restricts roles to `INVITABLE_ROLES` and says "role is required" when the role is missing.
  - `updateUser` only validates fields that are present in the request.
  - `createUser` defaults the role to `member`.
- **Possible existing bug, left alone:** `inviteUser` never lowercased the email, while `createUser` and `updateUser` do. So an invite for `Foo@x.com` isn't caught as a duplicate of an existing `foo@x.com`. I kept this by passing `{ lowercase: false }`. Removing that option makes invites lowercase the email like the other two. That would change what gets stored, so I left the call to you.