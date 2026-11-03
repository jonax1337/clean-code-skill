The email, name and role checks now live in one file, `src/validation/userFields.js`, and all three handlers use it. All 28 tests pass. I haven't committed anything.

**What's in the shared module**
- `checkEmail`, `checkName` and `checkRole` hold the rules and the exact message strings from `docs/api.md`. The email pattern, the 80-character limit and the role lists (`USER_ROLES`, and `INVITABLE_ROLES`, which is every role except owner) are each defined once.
- Two variants cover invitations: `checkOptionalName` (an empty name is allowed, the length limit still applies) and `checkRequiredRole` (reports "role is required").
- `collectResults` gathers the accepted values and the error messages in field order, so the documented email, name, role message order holds everywhere.

**What stays in each handler** is what's actually specific to it:
- `createUser`: the default role (`member`).
- `updateUser`: only the fields present in the request are checked, plus "no fields to update".
- `inviteUser`: optional name, required role, owner not allowed.
- The duplicate-email and not-found checks.

**One behaviour change:** `inviteUser` was the copy that had drifted. It didn't lowercase emails, although the docs say invitation emails are stored in lowercase. It now uses the same email check as the other two. So an invitation for `Bob@Example.com` is stored as `bob@example.com`, and a second invite for `BOB@example.com` now gets a 409 where before it went through. A new test covers this. Any invitations already stored in mixed case won't be changed. That only matters if the in-memory store is ever replaced with a database that keeps data.

**Tests added:** `test/userFields.test.js` covers each check directly. I also added handler tests for:
- message order
- `role: null` (still rejected, as before)
- an empty update body
- trying to invite someone as owner