The email, name and role checks now live only in `src/userValidation.js`, so a fix to one of them is made once. The work is in two commits on `main`, but they weren't pushed because the repo has no remote set up.

**How it works**
- Each field rule is written once: `email` (trimmed and lowercased, must not be blank, must look like `local@domain.tld`), `name` (trimmed, must not be blank, at most 80 characters) and `roleIn(allowed)`.
- What differs between endpoints is spelled out in one line each:
  - `validateNewUser`: the role defaults to `member`.
  - `validateUserChanges`: only the fields that are present get checked.
  - `validateInvitation`: the name can be blank, the role is required, and `owner` isn't allowed.
- The three handlers now just call their validator and keep their own 404, 409 and "no fields to update" logic.
- Messages are still collected in the order email, name, role, so the wording and order clients match on haven't changed.

**A bug the copies had already caused:** `inviteUser` trimmed the email but didn't lowercase it, although `docs/api.md` says invitation emails are stored lowercase. That meant you could invite `BOB@example.com` while `bob@example.com` already had a pending invitation. I added tests that showed this (one got `'Bob@Example.COM'`, the other got 201 instead of 409) and fixed it in its own commit before the extraction. Clients will now see invitation emails stored lowercase, which is what the docs promise.

**Testing**
- I added 9 tests that pin the documented rules: every message, their order, the 80-character limit, partial updates, and the invitation rules for name, role and `owner`. `npm test` passes 25/25 before and after the extraction.
- The crapper, dryer and mutator tools named in ub-mode aren't installed here, so I didn't run them. Instead I broke the new module by hand in 14 ways (flipped conditions, dropped normalization, swapped field order, wrong default role, `owner` allowed in invites), and a test failed for every one.

**Log**
1. Read the three handlers, the tests and `docs/api.md` (which is the contract), and confirmed the starting point: 16/16 passing.
2. Added the pinning tests. The 2 invitation tests failed because emails weren't lowercased.
3. Made `inviteUser` lowercase the email (25/25) and committed it as `c657c9d`.
4. Wrote `src/userValidation.js` and cut the three handlers down to use it. Simplified `required` and stopped exporting `ROLES` (25/25).
5. Ran the hand mutation pass: 14 of 14 broken versions were caught.
6. Added the new module to the README layout list and committed it as `d1bdd65`.
7. Tried to push, which failed: there's no `origin`. Once you add a remote, `git push origin main` will publish both commits.