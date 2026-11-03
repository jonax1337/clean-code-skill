I moved the email, name and role checks into one new module, `src/validation.js`. `createUser`, `updateUser` and `inviteUser` now call it instead of carrying their own copies. `npm test` passes: 21 tests, 16 existing plus 5 new ones for the module in `test/validation.test.js`. I haven't committed anything.

- **Shared checks:** the email pattern, the 80-character name limit, the role list and the message texts now live only in `src/validation.js`. A fix to any of them is made once.
- **What stays in each handler:** the defaults, the optional-field handling and the conflict checks.
  - `createUser` defaults the role to `member`.
  - `updateUser` only validates the fields that are present.
  - `inviteUser` makes the name optional, requires a role, and allows only the invitable roles.
- **Behavior:** unchanged.

**Possible bug I left alone:** `inviteUser` doesn't lowercase the email, but `createUser` and `updateUser` do. An invite for `Ann@x.com` therefore wouldn't conflict with an existing `ann@x.com`. I kept the current behavior because you didn't ask for a change. If you want it fixed, move the lowercasing into `validateEmail` so all three handlers behave the same. That would change what `inviteUser` stores, so it needs your call.