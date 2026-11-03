The email, name and role checks now live in one new file, `src/validation.js`, and `createUser`, `updateUser` and `inviteUser` all call it. All 19 tests pass. The commit is local only: `git push` failed because the repo has no remote or upstream configured, so nothing has been pushed.

**What changed**
- **Validators:** `src/validation.js` exports `validateEmail`, `validateName` and `validateRole`. Each returns `{ value }` or `{ error }`.
- **Handlers:** the three handlers keep only their own rules. `updateUser` runs the same validators in a loop over whichever fields are present.
- **Behavior:** unchanged. The 16 existing handler tests pass as before. I added `test/validation.test.js` with 3 tests that call the validators directly.

**Differences between the handlers**
- `inviteUser` doesn't lowercase emails, while the other two do. I kept that with `validateEmail(x, { lowercase: false })`. It looks like it could be an accident, since it means `A@x.io` and `a@x.io` count as different invitees. If so, delete that option and all three handlers behave the same.
- `inviteUser` accepts an empty name and only allows the roles admin, member and viewer. Those rules are passed in as options (`required: false` and the role list).

**Log**
1. Read the three handlers and ran the tests for a baseline (16 pass).
2. Wrote `src/validation.js` and rewired the handlers.
3. Added the validator tests and re-ran everything (19 pass).
4. Committed as `5a0b8f5`; the push failed as described above.

I skipped the crapper, dryer and mutator checks because I didn't have those tools here.