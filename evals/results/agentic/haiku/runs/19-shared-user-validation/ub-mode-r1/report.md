The user validation now lives in one module, `src/validation/user.js`. The three handlers call it, so a fix to the email, name or role rules is made once. All 18 tests pass, and the change is uncommitted.

**Changes**
- `src/validation/user.js` (new) holds the email pattern, the name length limit, the role lists, and the parsers `parseEmail`, `parseName` and `parseRole`. Each parser returns `{ value, messages }`, and `collectMessages` gathers the messages in the order the API doc specifies.
- `createUser`, `updateUser` and `inviteUser` only compose these parsers now. The policy stays in each handler: the `member` default on create, the invite-only role list, and the rule that a name is optional on invite.
- `inviteUser.test.js` has two new tests: an invite with a mixed-case email is stored in lowercase, and a 409 is returned when the email differs only in case from a user's email.

**Behaviour change**
- Invitation emails are now lowercased. The old `inviteUser` only trimmed them. `docs/api.md` says invitations are stored lowercase, and the case-sensitive lookup meant a mixed-case invite could slip past the duplicate check. This is the one intended change.

**Verification**
- I added the two invite tests first and confirmed they failed. Then I refactored and the suite went from 16 to 18 passing.
- I ran a differential check of the original `HEAD` handlers against the new ones over 44,244 request combinations. The only differences were invite requests with a non-lowercase email. Those differences are the fix above.

**Not done**
- I did not commit or push, since you didn't ask for that. The changes are in the working tree.
- I did not run the crapper, dryer or mutator tools from ub-mode. They aren't available in this repo, and the handler tests cover the parsers only indirectly.

**Log**
1. Read the handlers, store, helpers, tests and `docs/api.md`.
2. Ran `node --test`: 16 pass.
3. Added two invite tests and saw them fail.
4. Created `src/validation/user.js` and rewrote the three handlers to use it.
5. Ran `node --test`: 18 pass.
6. Ran the differential check against `HEAD` (in `C:\Users\Jonas\AppData\Local\Temp\ub-diff`, outside the repo): only the intended invite-email differences.