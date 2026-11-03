The email, name and role checks now live in one module, `src/validateUser.js`, and `createUser`, `updateUser` and `inviteUser` all use it. `npm test` passes with 25 tests: the original 16 plus 9 I added. I didn't run a linter or type check, and the project doesn't configure one.

**How it works**
- The module has `validateEmail`, `validateName`, `validateOptionalName` and `validateRole(input, allowedRoles)`. Each returns `{ value }` or `{ message }`. `collectMessages` gathers the failures.
- The module also holds the role lists. `INVITABLE_ROLES` is derived from `ROLES` minus `owner`, so the two can't drift apart.
- The handlers keep what is specific to them: `createUser` defaults the role to `member`, `inviteUser` requires a role and allows an empty name, and `updateUser` only validates the fields that are present.
- The message wording and the email, name, role order are unchanged, since `docs/api.md` says clients match on them.

**One behavior change:** `inviteUser` used to store the email without lowercasing it. `docs/api.md` says invitation emails are stored trimmed and lowercase, and the store's duplicate check compares exactly, so `Bob@x.com` and `bob@x.com` could both get invitations. It now lowercases like the other two, which matches the docs. I added a test for it.

**New tests:** `test/validateUser.test.js` covers the shared rules, including the 80 and 81 character name boundary. I also added two cases to `test/inviteUser.test.js`: the lowercase storage and rejecting the `owner` role.

I didn't touch `listUsers`, `deleteUser`, the store or the docs.