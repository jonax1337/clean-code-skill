The email, name and role checks now live in one new file, `src/validation.js`. `createUser`, `updateUser` and `inviteUser` all call it. I ran `npm test` and all 21 tests pass. That includes the existing handler tests, which I didn't change, and five new unit tests in `test/validation.test.js` for the shared validators.

The three validators are `validateEmail`, `validateName` and `validateRole`. Each returns `{ value }` or `{ error }`, so the handlers only collect messages and apply their own rules. Behavior is unchanged, including the ways the handlers differ:
- **`inviteUser` email:** it keeps the email's case, through `validateEmail(..., { lowercase: false })`. The other two lowercase it. This looks like it could be an accident, so you may want to decide whether invites should lowercase too. If so, it's a one-line change.
- **`inviteUser` name and role:** the name may be empty (`required: false`), the role is required, and only admin, member and viewer are allowed.
- **`updateUser`:** it only validates fields that are present in the request.

I left the duplicate-email checks in the handlers, since they depend on the store and differ per handler.