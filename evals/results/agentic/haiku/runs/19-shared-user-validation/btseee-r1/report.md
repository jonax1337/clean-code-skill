The user validation now lives in one module, `src/validation/userFields.js`. All 21 tests pass: the 16 existing ones plus 5 new ones.

**What's shared:** the email rules (trim, lowercase, format), the name rules (trim, 80-character limit), and role membership. A fix to any of these now happens in one place.

**What stays per handler:** the policy each endpoint applies.
- `createUser`: email and name required, role defaults to `member`, all four roles allowed.
- `updateUser`: each field is validated only when present.
- `inviteUser`: name optional, role required, `owner` not invitable.

**Behavior change to check:** `inviteUser` used to store the email as typed, so `Bob@Example.com` was saved as-is. It now lowercases it like the other two endpoints. I think that's the right behavior, since existing-user lookups compare lowercased emails, but it is a change. I added a test for it. If you'd rather keep the old behavior, tell me and I'll adjust.

**Other choices:**
- The `inviteUser` role check still reports `role is required` when the role is missing, as before.
- I added `test/userFields.test.js` for the shared rules and two invite tests (lowercasing and rejecting `owner`).
- I didn't commit anything.