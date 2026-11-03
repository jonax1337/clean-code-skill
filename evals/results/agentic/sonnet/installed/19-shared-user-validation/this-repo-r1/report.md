The email, name and role checks now live in one new module, `src/userFields.js`, and `createUser`, `updateUser` and `inviteUser` all use it. `npm test` passes with 19 tests: the 16 that were there plus 3 new ones for `inviteUser`. I did not run a linter, and the repo has no type check.

**Behaviour change in `inviteUser`:** it now lowercases the email, as the other two handlers already did. Before, it only trimmed. As a result, `ANN@example.com` is now caught as a duplicate of an existing `ann@example.com` user (409). It used to slip through and be stored in mixed case. `docs/api.md` doesn't say either way. I treated the old behaviour as the bug, since the point is one shared rule. If you want invitations to keep the original casing, say so and I'll add an exception.

**What's in the shared module:**
- `parseEmail`, `parseName`, `parseRole` and `parseOptionalName` each return `{ value }` or `{ error }`. The messages are unchanged.
- The email pattern, the role list and the 80-character limit exist only there.
- `parseOptionalName` is for invitations, where a missing or blank name is stored as `''`. It still enforces the length limit.

**What stays in each handler:**
- `createUser` keeps its default role (`member`).
- `inviteUser` keeps the "role is required" check and its own list of invitable roles (no `owner`).
- `updateUser` only validates the fields present in the body.
- The duplicate-email checks stay where they were. They query different stores, so they weren't shared.

The new tests cover the lowercasing, the optional name with its length limit, and rejecting `owner` as an invited role.