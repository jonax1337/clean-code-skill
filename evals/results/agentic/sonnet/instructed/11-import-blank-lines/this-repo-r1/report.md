`hourlog import` now skips blank lines, including whitespace-only ones, so the empty last line in your accountant's CSV no longer raises the error. I haven't run it against their actual file, only the tests: `pytest` shows 20 passed.

The importer split every line into three fields, so an empty line failed with the "expected 3, got 1" error. The fix is a two-line check in `parse_entries` in `hourlog/importer.py`.

Skipped blank lines still count towards line numbers. A bad row after a blank one is reported at its real line in the file.

I added two tests in `tests/test_importer.py`, one for skipping blank lines and one for the line numbering. I didn't confirm that the skipping test fails without the fix.

I left everything else in the importer alone. Malformed non-blank lines, such as a row with too few fields, still raise an error.