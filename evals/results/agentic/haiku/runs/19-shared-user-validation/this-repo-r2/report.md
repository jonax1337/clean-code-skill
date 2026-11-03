The email, name and role checks now live in one module, `src/validation.js`. A fix to any of them is made once, and all three handlers pick it up. All 25 tests pass (the original 16 plus 9 new ones).

**What changed**
- `src/validation.js` (new) holds `checkEmail`, `checkName`, `checkRole`, and `errorsOf`, which collects the messages. The email pattern, the 80-character limit and the role list are defined once.
- `createUser`, `updateUser` and `inviteUser` now call those checks. The rules that really differ stay in each handler: the create default role of `member`, the update rule of checking only fields that are present, the invite rule that a role is required and `owner` is not allowed, and the conflict checks.
- `test/validation.test.js` (new) pins the shared rules, including the 80-character limit on optional names, which no test covered before.

**Behavior check**
I ran the original and refactored handlers side by side on 70 inputs, covering null, non-string, empty, malformed, too-long, and unknown-role values. The results were identical in every case.

**Decision for you: invite email case**
`inviteUser` trims the email but does not lowercase it. `createUser` and `updateUser` lowercase it. So `Bob@Example.com` is stored as typed, and a later `bob@example.com` will not match it in the duplicate check. I kept this as it was, because changing it changes invitation behavior. The shared `checkEmail` takes a `{ lowercase: false }` option for invites. If this is a bug, one line in `inviteUser.js` fixes it, and it should get a test.

I did not commit anything.