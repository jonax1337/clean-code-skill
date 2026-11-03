## Review

**Bugs**
1. **Off-by-one:** `range(1, len(rows) - 1)` never imports the last row. A file with a header and 3 users imports only 2.
2. **Silent failures:** `except Exception: pass` hides malformed rows (`IndexError`), DB failures, and mailer failures. If `mailer.send` fails after `db.save`, the user is saved but missing from `imported`, so the return value is wrong.

**Design**
3. **Duplicated decision:** `"@" not in email or len(email) > 254` re-implements `is_valid_email`. Use the existing function. If it doesn't enforce the 254 limit, add that there, not here.
4. **Dead code:** the `# old version` comment should be deleted. Git history already has it.
5. **Mixed concerns:** parsing and validation are pure and should be separate from the DB and mail side effects.
6. **Not idempotent:** re-running the same file saves duplicate users. I can't see the `db` API, so I haven't changed this, but I'd dedupe by email (an upsert or a unique constraint) in a follow-up.

## Failing test first

```python
def test_imports_every_data_row_including_last(monkeypatch):
    saved = []
    monkeypatch.setattr(importer.db, "save", saved.append)
    rows = [
        ["first", "last", "email"],
        ["Ann", "A", " ANN@x.com "],
        ["Bob", "B", "bob@x.com"],
        ["Cy", "C", "cy@x.com"],
    ]
    result = importer.import_users(rows)
    assert [u.email for u in result] == ["ann@x.com", "bob@x.com", "cy@x.com"]
    assert saved == result

def test_bad_rows_are_skipped_and_logged(monkeypatch, caplog):
    monkeypatch.setattr(importer.db, "save", lambda u: None)
    rows = [["h", "h", "h"], ["Ann", "A"], ["Bob", "B", "not-an-email"], ["Cy", "C", "cy@x.com"]]
    result = importer.import_users(rows)
    assert [u.email for u in result] == ["cy@x.com"]
    assert "row 2" in caplog.text and "row 3" in caplog.text

def test_mail_failure_keeps_saved_user(monkeypatch):
    monkeypatch.setattr(importer.db, "save", lambda u: None)
    def boom(*a): raise RuntimeError("smtp down")
    monkeypatch.setattr(importer.mailer, "send", boom)
    result = importer.import_users([["h", "h", "h"], ["Ann", "A", "a@x.com"]], send_welcome=True)
    assert len(result) == 1
```

The first test should fail on the current code because `cy@x.com` is dropped. The other two fail because errors are swallowed without logging and a mail failure loses the user.

## Proposed change

```python
import logging
from utils.validation import is_valid_email

log = logging.getLogger(__name__)


def parse_row(row):
    """Pure: return (name, email) or raise ValueError/IndexError."""
    first, last, raw_email = row[0], row[1], row[2]
    email = raw_email.strip().lower()
    if not is_valid_email(email):
        raise ValueError(f"invalid email {raw_email!r}")
    return f"{first} {last}".strip(), email


def import_users(rows, send_welcome=False):
    imported = []
    for line, row in enumerate(rows[1:], start=2):  # rows[0] is the header
        try:
            name, email = parse_row(row)
        except (IndexError, ValueError) as e:
            log.warning("row %d skipped: %s", line, e)
            continue

        user = User(name=name, email=email)
        try:
            db.save(user)
        except Exception:
            log.exception("row %d: save failed", line)
            continue
        imported.append(user)

        if send_welcome:
            try:
                mailer.send(email, "Welcome!", WELCOME_TEMPLATE)
            except Exception:
                log.exception("row %d: welcome mail failed", line)
    return imported
```

## Notes
- I kept the return type (`list[User]`) so callers don't break. If callers need to know which rows were skipped, a follow-up could return a result object with `imported` and `skipped`.
- Decision for you: a `db.save` failure is now logged and the import continues, as before but visibly. If you'd rather abort the whole import, remove that `try`.
- Verify that `is_valid_email` accepts the same inputs as the old check. It's probably stricter, which is likely intended.
- I couldn't run the tests, the crapper, dryer, or mutator tools, or commit anything here (no tools, not a git repo). The tests above are unrun, and `parse_row` is small enough that I expect it to be under CRAP 10.

## Log
1. Read the diff and found the off-by-one, because it silently loses data.
2. Found the swallowed exceptions and the inconsistent mail/save state, because the return value can be wrong.
3. Replaced the inline email check with `is_valid_email`, so the decision lives in one place.
4. Extracted pure `parse_row` to separate validation from side effects.
5. Deleted the dead commented-out code.
6. Wrote three behavior tests that call `import_users` as a caller would.
7. Flagged idempotency and the return shape as follow-ups instead of widening this change.

Suggested commits, in order: tests, then the off-by-one fix, then validation reuse with `parse_row` and logging, then removal of the dead comment.