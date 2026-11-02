## Review

**Bugs**

1. **Off-by-one: the last data row is never imported.** `range(1, len(rows) - 1)` stops one row early. Use `rows[1:]`.
2. **`except Exception: pass` hides every failure.** A bad row, a DB outage and a mailer error all vanish. Worse, if `mailer.send` fails after `db.save`, the user is persisted but missing from `imported`, so the return value no longer matches the database.
3. **Skipped rows are silent.** The caller can't tell that 40 of 100 rows were dropped.

**Clean-code issues**

- Email validation is reimplemented (`"@" not in email`, `len > 254`) even though `is_valid_email` exists. The inline check is also weaker.
- `row[0]`, `row[1]` and `row[2]` are magic indexes.
- `# skip header` and the "old version" comment are noise. Git history already keeps the old version.
- The function parses, validates, persists and notifies all in one loop.

## Suggested change

```python
import logging

from utils.validation import is_valid_email

logger = logging.getLogger(__name__)

FIRST_NAME_COLUMN = 0
LAST_NAME_COLUMN = 1
EMAIL_COLUMN = 2


def import_users(rows, send_welcome=False):
    imported = []
    for row_number, row in enumerate(rows[1:], start=2):  # rows[0] is the header
        try:
            user = _build_user(row)
        except ValueError as error:
            logger.warning("Skipping row %d: %s", row_number, error)
            continue

        db.save(user)
        imported.append(user)
        if send_welcome:
            _send_welcome(user)
    return imported


def _build_user(row):
    try:
        first_name = row[FIRST_NAME_COLUMN]
        last_name = row[LAST_NAME_COLUMN]
        raw_email = row[EMAIL_COLUMN]
    except IndexError:
        raise ValueError("expected at least 3 columns")

    email = raw_email.strip().lower()
    if not is_valid_email(email):
        raise ValueError(f"invalid email {email!r}")
    return User(name=f"{first_name} {last_name}", email=email)


def _send_welcome(user):
    try:
        mailer.send(user.email, "Welcome!", WELCOME_TEMPLATE)
    except Exception:
        logger.exception("Welcome email failed for %s", user.email)
```

## Behavior changes to confirm

- **The last row is now imported.** This is the bug fix, but it changes output for existing callers.
- **`db.save` errors now propagate** instead of being swallowed. If you'd rather keep going past a failed row, catch the DB's specific exception around `db.save` and log it. Avoid a bare `Exception`.
- **Mailer failures are logged but don't undo the import.** The user is already saved, so they stay in `imported`. If you narrow the `except` to the mailer's real exception type, that's even better.
- **Validation may differ.** Check that `is_valid_email` covers the 254-character limit. If it doesn't, add the limit there rather than inline.
- **Consider returning skipped rows too**, for example as a result object, if callers need to report them.

## Tests worth adding

- The last row is imported.
- The header row is skipped.
- A short row is skipped and logged.
- An invalid email is skipped.
- With `send_welcome=True`, a mailer failure still returns the user.
- With `send_welcome=False`, the mailer is never called.