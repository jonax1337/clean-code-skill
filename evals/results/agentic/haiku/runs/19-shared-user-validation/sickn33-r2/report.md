The email, name and role rules now live in one module, `src/validation/userFields.js`. `createUser`, `updateUser` and `inviteUser` all call it, so a rule fix only has to go in one place. The 16 existing tests pass, and the old and new handlers returned identical responses across 29 edge-case inputs.

**What changed**
- `userFields.js` exports `checkEmail`, `checkName`, `checkRole`, plus the `ROLES`, `INVITABLE_ROLES` and `MAX_NAME_LENGTH` constants. Each check returns either `{ value }` or `{ message }`.
- The handlers keep their own control flow: which fields are required, which role list applies, and the conflict checks. Those differ per endpoint, so I didn't force them into the shared module.
- I didn't commit anything.

**Decision for you: email casing in invites**
`createUser` and `updateUser` lowercase emails, but `inviteUser` only trims them. So `Bob@Example.COM` is stored as `bob@example.com` when a user is created but kept as `Bob@Example.COM` when invited. The store compares emails case-sensitively, so the same address could pass the duplicate check in one place and fail it in the other. I preserved the current behavior with a `{ lowercase: false }` option and left a comment. If invites should lowercase too, it's a one-line change in `inviteUser.js`, but it would change what gets stored, so I didn't make it without asking.