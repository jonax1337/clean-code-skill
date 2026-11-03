# Member API

Every handler returns `{ status, body }`. Clients match on the strings in `messages`, so their wording is part of
the contract and must not change.

## Conventions

- Email addresses are matched case-insensitively. They are stored trimmed and in lowercase, whether they belong
  to a user or to an invitation.
- Names are stored trimmed and may be at most 80 characters.
- Roles are `owner`, `admin`, `member` and `viewer`.
- When validation fails the status is `400` and the body is `{ "error": "validation_failed", "messages": [...] }`.
  Every failing field adds one message; the order is email, name, role.
- `404` is `{ "error": "not_found", "message": "user not found" }`, `409` is
  `{ "error": "conflict", "message": "email already in use" }`.

## Validation messages

| Field | Rule | Message |
| --- | --- | --- |
| email | missing, not a string or blank | `email is required` |
| email | not of the form `local@domain.tld` | `email is invalid` |
| name | missing, not a string or blank | `name is required` |
| name | longer than 80 characters | `name must be at most 80 characters` |
| role | not one of the roles above | `role is invalid` |

## POST /users (createUser)

Body: `email`, `name`, optional `role`. The role defaults to `member`. Responds `201` with the user. Answers `409`
when a user with that email exists.

## PATCH /users/:id (updateUser)

Accepts partial input: only the fields that are present are validated and changed, and a field that is present is
held to the same rules as when creating. A body without any of the three fields is rejected with the single
message `no fields to update`. Answers `404` for an unknown id and `409` when the email belongs to another user.
Responds `200` with the updated user.

## POST /invitations (inviteUser)

Body: `email`, `role`, optional `name`. The invitee fills in their name when they accept, so the name may be
missing or empty (it is then stored as an empty string); a name that is given must still be at most 80
characters. The role is required (`role is required`) and `owner` cannot be granted by invitation: it is rejected
with `role is invalid`. Answers `409` when a user or a pending invitation with that email exists. Responds `201`
with the invitation, which has the status `pending`.

## GET /users (listUsers)

Query: `q` (matches name or email), `limit` (1 to 100, default 25), `offset` (default 0). Invalid paging values
answer `400` with `limit must be between 1 and 100` or `offset must be 0 or greater`.

## DELETE /users/:id (deleteUser)

Responds `204`. Answers `404` for an unknown id and `409` with `cannot delete the last owner` when the user is
the only owner.
