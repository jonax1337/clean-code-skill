`hourlog import` now skips blank lines, so the trailing empty line in your accountant's CSV no longer causes the error. The full test suite passes (19 tests). I didn't run the import on your actual CSV file.

The fix is a check at the top of the loop in `parse_entries` (`hourlog/importer.py`). Lines that are empty or only whitespace are skipped. Line numbers still count the blank lines, so an error on a real line still points to the right place in the file.

I added a test in `tests/test_importer.py` for blank lines in the middle and at the end of a file, and for the line numbers staying correct after a blank line.