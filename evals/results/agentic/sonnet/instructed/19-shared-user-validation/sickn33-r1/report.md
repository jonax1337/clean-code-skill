The email, name and role checks now live in one new module, `src/userValidation.js`, and `createUser`, `updateUser` and `inviteUser` all call it. All 16 existing tests pass. I haven't committed anything.

- **Shared parsers:** `parseEmail`, `parseName` and `parseRole` hold the trimming, patterns, the 80-character limit and the error messages. `collectFields` gathers the results into valid values and error messages.
- **Handlers:** each one now only decides which fields apply and what to do with the result. `updateUser` parses only the fields present in the request.
- **Behaviour:** I kept it the same. The three places differed in a few ways, so these are options on the shared parsers:
  - `inviteUser` makes the name optional.
  - `inviteUser` requires a role and only allows `admin`, `member` or `viewer`.
  - `createUser` defaults the role to `member`.

**Possible bug:** `inviteUser` does not lowercase the email, while `createUser` and `updateUser` do. The store compares emails exactly. So inviting `Ann@Example.com` won't conflict with an existing `ann@example.com`, and the invitation keeps the mixed case. I kept this as it was, using `parseEmail(..., { lowercase: false })`. If it's a bug, removing that option fixes it everywhere. Do you want me to make that change?

The tests don't cover the parsers directly. I can add unit tests for `userValidation.js` if you want them.