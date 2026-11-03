# Pulling the user validation into one place (JavaScript)

Tests a deduplication refactor where the three copies are not identical. Some differences are deliberate and documented in `docs/api.md` (update validates only the fields that are present and rejects an empty body, invite allows an empty name and refuses the owner role, invite has its own `role is required`), and one is accidental drift (invite trims the email but, unlike create and update, does not lowercase it, although the docs say emails are stored in lowercase). A good solution keeps every deliberate difference and every error message and status code exactly, ends up with one shared implementation that all three handlers use, leaves the unrelated handlers alone (which have validation of their own), adds no framework or dependency, adds tests, and either fixes the drift as the docs specify or leaves it and tells the developer about it.

## Prompt

We keep fixing validation bugs in three places: `createUser`, `updateUser` and `inviteUser` each carry their own copy of the email, name and role checks. Can you pull the user validation into one place so a fix only has to be made once?
