# adminhub

Small user-admin service for our internal console. It keeps users in SQLite and exposes plain handler functions
(`adminhub/api.py`) that the web layer calls with the decoded request parameters and turns into HTTP responses.

## Handlers

| Handler | Parameters | Result |
| --- | --- | --- |
| `get_user` | `id` | 200 with the user, 404 if unknown |
| `list_users` | none | 200 with all users, ordered by id |
| `deactivate_user` | `id` | 200, 404 if unknown |
| `signups` | `start`, `end` (ISO dates, `end` exclusive) | 200 with signups per day |

Paged endpoints take `page` and `per_page`; **pages are numbered from 1**.

## Development

```
python -m pytest -q
```

All queries go through `sqlite3` with `?` placeholders. Pull requests are reviewed from the patch under `pr/`.
