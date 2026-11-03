`hourlog import` now skips blank lines, so the accountant's CSV should import. The full test suite passes (20 tests). I haven't run it on the accountant's actual file.

The importer split every line on commas, and an empty line splits into one empty value. That's why you saw "expected 3, got 1". The fix is in `parse_entries` in `hourlog/importer.py`. It skips lines that are empty or only whitespace. Line numbers in error messages still count the blank lines, so "line 41" will still match the line in the file.

I added two tests in `tests/test_cli.py`. One checks that blank lines in the middle and at the end are ignored. The other checks that an error after a blank line reports the right line number.

I didn't commit anything.