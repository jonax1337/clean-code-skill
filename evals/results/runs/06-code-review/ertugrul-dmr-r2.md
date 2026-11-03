# Review: `import_users`

## Bug

- **G3 (boundary condition): the last data row is never imported.** `range(1, len(rows) - 1)` stops one short. With a header and 3 data rows, only 2 are processed. Use `rows[1:]`.

## Clean Code violations

- **G5 (duplication):** `"@" not in email or len(email) > 254` reimplements `is_valid_email`. Use the existing helper.
- **F3 (flag argument):** `send_welcome` makes the function do two things. Split it.
- **G4 / G26 (imprecise, safeties overridden):** `except Exception: pass` hides every failure, including bugs and DB outages. It also leaves inconsistent state: if `mailer.send` fails after `db.save`, the user is saved but missing from `imported`.
- **C5:** Delete the `# old version:` commented-out code. Git has it.
- **C3:** `# skip header` is replaced by self-explanatory code (`rows[1:]`).
- **G25 / P2:** The magic column indices `0`, `1`, `2` should be named constants.
- **G30 / G34 (one thing, one abstraction level):** The function parses, validates, persists, and emails. Extract the parsing and the email step.
- **G19:** Introduce an explanatory variable for the full name instead of inline concatenation.
- **P3:** Add type hints on the public interface.

## Suggested revision

```python
import logging

from utils.validation import is_valid_email

logger = logging.getLogger(__name__)

FIRST_NAME_COLUMN = 0
LAST_NAME_COLUMN = 1
EMAIL_COLUMN = 2
MIN_COLUMNS = EMAIL_COLUMN + 1


def import_users(rows: list[list[str]]) -> list[User]:
    data_rows = rows[1:]
    users = (_parse_user(row) for row in data_rows)
    return [_save(user) for user in users if user is not None]


def import_users_and_send_welcome(rows: list[list[str]]) -> list[User]:
    imported = import_users(rows)
    for user in imported:
        mailer.send(user.email, "Welcome!", WELCOME_TEMPLATE)
    return imported


def _parse_user(row: list[str]) -> User | None:
    if len(row) < MIN_COLUMNS:
        logger.warning("Skipping malformed row: %r", row)
        return None

    email = row[EMAIL_COLUMN].strip().lower()
    if not is_valid_email(email):
        logger.warning("Skipping row with invalid email: %r", email)
        return None

    full_name = f"{row[FIRST_NAME_COLUMN]} {row[LAST_NAME_COLUMN]}"
    return User(name=full_name, email=email)


def _save(user: User) -> User:
    db.save(user)
    return user
```

Fixed:
- Off-by-one that dropped the last row (G3)
- Duplicated email validation, now using `is_valid_email` (G5)
- Flag argument split into two functions (F3)
- Swallowed exceptions replaced by explicit malformed-row handling plus logging (G4, G26)
- Commented-out code and the redundant comment removed (C5, C3)
- Column indices extracted to named constants (G25)
- Responsibilities split (G30), explanatory variable added (G19), type hints added (P3)

## Points to confirm

1. **Error handling change:** DB errors now propagate instead of being silently skipped. If you want partial imports to continue, catch your DB layer's specific exception around `_save` and log it. Avoid a bare `Exception`.
2. **Email timing:** Welcome emails now go out after all users are saved, which avoids sending mail for a row whose save later fails. Check that this ordering is acceptable.
3. **Validator input:** I pass the normalized (stripped, lowercased) email to `is_valid_email`. Confirm that matches what the helper expects, and that it enforces the 254-character limit. If it doesn't, add that check there rather than here.

## Tests to add (T5)

- Empty `rows` and a header-only list
- Last row is imported (regression for the off-by-one)
- Row with fewer than 3 columns
- Invalid email, and an email of exactly 254 and 255 characters
- Whitespace and mixed-case email is normalized
- Welcome variant sends exactly one email per imported user and none for skipped rows