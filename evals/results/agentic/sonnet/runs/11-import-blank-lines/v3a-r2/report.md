`hourlog import` now skips empty lines, so the trailing blank line in your accountant's CSV no longer causes the "not enough values to unpack" error. I didn't run it on the accountant's actual file. The full test suite passes (19 tests, via `pytest`).

The fix is in `parse_entries` in `hourlog/importer.py`. Lines that are empty or only whitespace are skipped. Skipped lines still count toward line numbers, so an error on a later line still points at the right place in the file.

I added a test in `tests/test_importer.py` covering blank lines in the middle and at the end of the input, and checking that a bad line after them reports the correct line number.

Non-blank lines that are malformed are still rejected as before.