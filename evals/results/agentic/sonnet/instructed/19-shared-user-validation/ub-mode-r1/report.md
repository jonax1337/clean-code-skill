The email, name and role checks now live in one new file, `src/validateUser.js`. `createUser`, `updateUser` and `inviteUser` all call it. The 16 existing tests pass. I didn't add new tests, because the existing handler tests already cover the behavior I preserved. I haven't committed anything.

The shared file has `validateEmail`, `validateName` and `validateRole`, plus a small `collect` helper that gathers the values and error messages. The email pattern, the 80-character name limit and the role lists are defined only there.

The handlers had a few real differences, which I kept as options on the shared validators rather than unifying:
- **`inviteUser` name:** it can be empty, via `validateName(..., { required: false })`.
- **`inviteUser` role:** it is required and can't be `owner`.
- **`updateUser`:** it only validates the fields that are present.
- **`inviteUser` email case:** it doesn't lowercase the email, unlike the other two. That looks like an accident to me, since `Bob@x.com` could be invited and then created as a second `bob@x.com`. I kept it as it was, via `{ lowercase: false }`. Removing that option is a one-line fix if you agree, but it changes behavior, so I left the decision to you.