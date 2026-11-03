`hourlog import` now skips blank lines, so the empty last line in your accountant's file no longer causes an error. The full test suite passes (20 tests).

The cause was in `hourlog/importer.py`: `_parse_line` split every line on commas, and an empty line becomes one field, which is the "expected 3, got 1" error. The parser now skips lines that are empty or contain only whitespace. Line numbers still count the skipped lines, so a real bad line later in the file is still reported with its actual line number.

Changes:
- **`hourlog/importer.py`**: skip blank lines in `parse_entries`.
- **`tests/test_importer.py`**: added tests for blank lines (including `\r\n` and whitespace-only lines) and for a bad line after blank lines keeping its line number.
- **`README.md`**: one sentence noting that blank lines are skipped.

I haven't run it against the accountant's actual file. The fix is for blank lines only; if the file has other quirks, such as a header row, the import will still stop with a line-numbered error. Nothing is committed.