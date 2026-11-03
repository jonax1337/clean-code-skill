# Review: `import_users`

## Findings

1. **Bug: the last row is dropped.** `range(1, len(rows) - 1)` stops one row early. A 3-row file (header + 2 users) imports only one user.
2. **Bug: `except Exception: pass` hides every failure.** Short rows (`IndexError`), DB errors and mailer errors all vanish silently. If `mailer.send` fails after `db.save`, the user is saved but missing from `imported`, so the return value no longer matches the DB.
3. **Duplicated decision.** `"@" in email and len <= 254` re-implements `is_valid_email`, and it's weaker (`"@"` and `a@@b` both pass). Validation should live in one place.
4. **Dead code.** The `# old version` comment should go; git already has it.
5. **Smaller issues:** names aren't stripped (only the email is), and `row[0] + " " + row[1]` produces `"Ann "` when the last name is empty.
6. **Not idempotent.** Re-running the same file creates duplicate users. I can't see `db` or `User`, so I'm flagging it rather than guessing at a fix (an upsert or unique-email check is probably the right one).

## Failing tests first

```python
def test_last_row_is_imported(fake_db, fake_mailer):
    rows = [["first","last","email"], ["A","B","a@x.com"], ["C","D","c@x.com"]]
    assert [u.email for u in import_users(rows)] == ["a@x.com", "c@x.com"]

def test_invalid_and_short_rows_are_skipped_not_fatal(fake_db, fake_mailer):
    rows = [["h","h","h"], ["A","B","a@@x"], ["C"], ["E","F","e@x.com"]]
    assert [u.email for u in import_users(rows)] == ["e@x.com"]

def test_mailer_failure_keeps_saved_user(fake_db, failing_mailer):
    rows = [["h","h","h"], ["A","B","a@x.com"]]
    assert [u.email for u in import_users(rows, send_welcome=True)] == ["a@x.com"]
```

The first test fails on the off-by-one. The third fails today because the user is saved but not returned.

## Suggested change

```python
import logging
from utils.validation import is_valid_email

log = logging.getLogger(__name__)

def _parse_row(row):
    """Pure: return (name, email), or None if the row is unusable."""
    if len(row) < 3:
        return None
    first, last, email = (cell.strip() for cell in row[:3])
    email = email.lower()
    if not is_valid_email(email):
        return None
    return f"{first} {last}".strip(), email

def import_users(rows, send_welcome=False):
    imported = []
    for line_no, row in enumerate(rows[1:], start=2):   # skip header
        parsed = _parse_row(row)
        if parsed is None:
            log.warning("import_users: row %d skipped (invalid)", line_no)
            continue
        name, email = parsed
        user = User(name=name, email=email)
        db.save(user)                    # DB errors propagate: fail loudly
        imported.append(user)
        if send_welcome:
            try:
                mailer.send(email, "Welcome!", WELCOME_TEMPLATE)
            except Exception:
                log.exception("import_users: welcome mail failed for row %d", line_no)
    return imported
```

## Why

- **Parse is separate from side effects.** `_parse_row` is pure and easy to test, and bad input is rejected at the boundary.
- **Bad rows are logged and skipped.** Only mailer failures are caught, because a failed email shouldn't undo a saved user. DB errors now propagate instead of being hidden.
- **Decision for you:** a DB error now aborts the batch, and since the import isn't idempotent, a re-run would duplicate the users already saved. If you'd rather continue past DB failures, catch the specific DB exception, log it, and continue. Otherwise, add the unique-email check from point 6.
- **Check `is_valid_email`:** if it doesn't enforce the 254-character limit, add that inside it rather than here.

## Action log

- Read the diff and identified the off-by-one, the swallowed exceptions and the duplicated validation.
- Wrote the tests first (they'd fail on the current code) and made the smallest restructuring that fixes the root causes.
- Removed the dead comment.
- I couldn't run anything here, so the tests, CRAP, dryer and mutator checks are still to do on your side. I also haven't committed anything. Suggested commits: (1) tests, (2) fix slice and error handling, (3) use `is_valid_email`.