`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer triggers the error. I ran `python -m pytest -q` and all 20 tests pass. I didn't run the import on the real CSV, since I don't have that file.

The parser was splitting every line on commas, and an empty line gives one value instead of three, hence "expected 3, got 1". The fix is in `parse_entries` in `hourlog/importer.py`. Lines that are empty or only whitespace (including a bare `\r\n`) are skipped.

Line numbers in error messages still count the skipped blank lines, so they match what you see in an editor. I added two tests to `tests/test_importer.py`: one that blank lines are skipped, and one that a bad line after a blank one is reported with the right number.

I haven't committed anything.