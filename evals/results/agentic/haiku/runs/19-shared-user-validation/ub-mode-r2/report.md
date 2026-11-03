The user validation now lives in one module, `src/validation.js`. A fix to the email, name or role rules is made once and reaches all three handlers.

**What changed**
- `src/validation.js` holds the rules: `validateEmail`, `validateName`, `validateRole`, plus the role lists.
- Each handler now only states its own policy. `createUser` requires the name and defaults the role to `member`. `updateUser` checks only the fields that are present. `inviteUser` makes the name optional and allows only the invitable roles.
- The rules the handlers still own, such as the default role and the presence checks, stay in the handlers because they differ per operation.

**One behavior change, which you should know about:** `inviteUser` did not lowercase the email, so inviting `Ann@Example.com` when `ann@example.com` already existed returned 201 instead of 409. I aligned it with the other two handlers, which fixes that. I pinned it with a test that failed before the change and passes after. I also added one sentence to `docs/api.md` for the invitations endpoint.

**Verification**
- All 17 tests pass (the original 16 plus the new one).
- I ran the original `HEAD` handlers against the new ones over 720 combinations of email, name and role. `createUser` and `updateUser` gave identical results in every case. `inviteUser` differed only in the mixed-case email case described above.

**Log of actions**
1. Read the three handlers, the tests, `response.js`, `store.js` and the API docs.
2. Ran the baseline suite: 16 passing.
3. Created branch `consolidate-user-validation` (we were on `main`).
4. Added the failing invite conflict test and confirmed it fails with 201 instead of 409.
5. Created `src/validation.js` and rewrote the three handlers on top of it.
6. Ran the suite (17 passing) and the differential check, then deleted the temporary old-code copy.
7. Updated `docs/api.md`.
8. Committed as `143de8b` ("Move user field rules into one validation module"), with the author set to your configured git identity.

**Not done**
- I did not push the branch. Pushing is outward-facing, so I left that for you.
- The ub-mode skill mentions Crapper, Dryer and Mutator tools. None are available in this repo, so I did not run them and I did not check complexity or duplication metrics. The check I did run was the differential comparison above.