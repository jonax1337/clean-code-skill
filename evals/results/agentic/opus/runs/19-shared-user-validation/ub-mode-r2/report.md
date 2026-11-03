The email, name and role checks now live in one place, `src/validation/userFields.js`. A fix to any of them only needs to be made there. All 24 tests pass and the work is committed on `main`. There's no git remote, so nothing was pushed.

**How it's set up**
- There's one rule each for `email()`, `name()` and `role()`, plus `validateFields(body, rules, { partial })`, which runs them in order and collects the error messages.
- Each handler now just declares which rules it uses and how it differs:
  - `createUser` uses all three rules, with role defaulting to `member`.
  - `updateUser` uses the same rules but only checks fields that are present (`partial: true`).
  - `inviteUser` doesn't require a name, requires a role, and only allows `INVITABLE_ROLES`, which excludes `owner`.
- Error messages, their order and the HTTP responses are exactly as before.

**One thing you should decide:** `inviteUser` trims the email but doesn't lowercase it, while users' emails are lowercased. So inviting `Ann@example.com` when `ann@example.com` is already a user slips past the duplicate check. That looks like one of the bugs you've been chasing. I kept the current behaviour, but it's now visible as `email({ lowercase: false })` with a comment. Fixing it means deleting that option and adding a test. Want me to do that?

**What I did**
1. Read the three handlers and listed where they really differ (name required or not, role default and allowed values, partial updates, lowercasing).
2. Added `test/userValidation.pin.test.js` with 8 tests covering paths the existing tests missed, and ran them against the old code: 24/24 passed. Committed as `e47b5b1`.
3. Wrote the shared module and rewired the three handlers to use it. The tests passed again, unchanged.
4. The skill's crapper, dryer and mutator tools don't come with it, so I tested by hand instead: I made 9 deliberate breaking changes to the shared module and the tests caught every one.
5. Committed the refactor as `b0a8328`.