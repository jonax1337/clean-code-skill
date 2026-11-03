# member-api

Request handlers for the member directory API: creating, updating, inviting, listing and deleting users.
Handlers are plain functions that take the in-memory store and a request and return `{ status, body }`; the
HTTP layer that calls them lives in another repository.

The behavior clients can rely on, including the exact error messages, is described in `docs/api.md`.

## Layout

- `src/handlers/` one file per endpoint
- `src/response.js` helpers that build `{ status, body }` results
- `src/store.js` the in-memory store
- `src/routes.js` the route table
- `test/` tests, one file per handler

## Tests

Node 20 or newer, no dependencies to install:

```
npm test
```
