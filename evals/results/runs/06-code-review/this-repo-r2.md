## Review

I couldn't run anything, and I haven't seen `is_valid_email`, `User`, `db` or `mailer`, so some points below are questions.

### Must change

**1. The last data row is never imported.**
`for i in range(1, len(rows) - 1):  # skip header`
`range` already excludes its upper bound, so `- 1` drops the final row. A 3-row file (header plus 2 users) imports only one user. Iterate over `rows[1:]` instead, which also makes the `# skip header` comment unnecessary.

**2. `except Exception: pass` hides every failure.**
```python
        except Exception:
            pass
```
This one handler covers a short row (`IndexError`), a DB outage, and a mailer failure, and reports none of them.
- If `db.save(user)` succeeds and `mailer.send(...)` then fails, the user is in the database but missing from `imported`, with no trace of why.
- If the database is down, the function returns `[]` as if the file were empty.
- A bug in `User(...)` looks the same as a bad row.

Handle the expected bad input explicitly, which is a short row or an invalid email, and log it with the line number. Let infrastructure errors propagate, or catch only the mailer's specific exception if a failed welcome email shouldn't abort the import.

**3. Email validation duplicates `utils/validation.py`.**
`if "@" not in email or len(email) > 254:`
This is a weaker, private copy of `is_valid_email`. It accepts `"@"`, `"a@"` and `"a b@c"`. Use the existing helper. Please check whether it already enforces the 254-character limit. If it doesn't, add the limit there rather than here. Also check whether it expects normalized input, since the code lowercases before validating.

### Should change

**4. Invalid rows are skipped silently.** The bare `continue` leaves the caller unable to tell "imported 90 of 100" from "imported 100 of 100". At minimum log a warning with the line number, and avoid logging the address itself. If callers need the list, returning rejected rows would be better, but that changes the public return type, so treat it as a suggestion.

**5. Delete the commented-out code.**
`# old version:` and `# for row in rows: db.save(User(...))` are dead code. Git has the history.

**6. Magic column indexes.** `row[0]`, `row[1]` and `row[2]` hide the file layout. Name them (`FIRST_NAME, LAST_NAME, EMAIL = 0, 1, 2`), or use `csv.DictReader` if the source is a CSV. `f"{row[0]} {row[1]}"` also reads better than the concatenation.

### Suggestions

- `send_welcome=False` is a flag argument. It makes the function both import and send mail. Returning the imported users and letting the caller send would be cleaner, but it changes the signature, so only do it if the callers are easy to update.
- I can't tell from the diff how duplicates are handled. Re-importing the same file would create duplicate users unless `db` has a unique constraint on email. Is that intended?
- The import is not atomic. A mid-file failure leaves a partial import. Is that acceptable?

### Suggested shape

```python
import logging

from utils.validation import is_valid_email

logger = logging.getLogger(__name__)

FIRST_NAME, LAST_NAME, EMAIL = 0, 1, 2
EXPECTED_COLUMNS = 3


def import_users(rows, send_welcome=False):
    imported = []
    for line_number, row in enumerate(rows[1:], start=2):  # rows[0] is the header
        if len(row) < EXPECTED_COLUMNS:
            logger.warning("Skipping line %d: expected %d columns, got %d",
                           line_number, EXPECTED_COLUMNS, len(row))
            continue
        email = row[EMAIL].strip().lower()
        if not is_valid_email(email):
            logger.warning("Skipping line %d: invalid email", line_number)
            continue
        user = User(name=f"{row[FIRST_NAME]} {row[LAST_NAME]}", email=email)
        db.save(user)
        imported.append(user)
        if send_welcome:
            mailer.send(email, "Welcome!", WELCOME_TEMPLATE)
    return imported
```

### Tests that would catch these

- The header plus two valid rows returns two users. This fails today because of the off-by-one.
- A header-only list and an empty list both return `[]`.
- A short row is skipped and the following valid row is still imported.
- An invalid email such as `"a@"` or `"a b@c.com"` is skipped. Also cover an address of exactly 254 characters (accepted) and 255 (rejected).
- Input like `"  Bob@Example.COM "` is saved as `bob@example.com`.
- With `send_welcome=True`, the mailer is called once per imported user. With `False`, it is never called.
- If `db.save` raises, the error reaches the caller instead of returning `[]`.
- If `mailer.send` raises, the behavior you decide on is pinned.

### What's good

Normalizing the email (`strip().lower()`) before validating and saving is the right order. Skipping bad rows instead of aborting the whole import is a reasonable policy once it is logged. The function is also short and easy to follow.