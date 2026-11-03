`hourlog import` now skips blank lines, so the trailing empty line in your accountant's CSV no longer causes the error. I ran `python -m pytest -q` and all 19 tests pass. I haven't run the import on your actual CSV.

The parser in `hourlog/importer.py` tried to read every line as `date,project,minutes`. An empty line splits into one value instead of three, which is the "expected 3, got 1" error. `parse_entries` now skips any line that is empty or only whitespace. Skipped lines still count toward line numbers, so an error on a later line still points at the right line in the file.

I added `test_blank_lines_are_skipped_but_still_counted` in `tests/test_importer.py`. It checks that blank lines are ignored and that an error after one is reported with the correct line number. I didn't confirm that the test fails without the fix.

I didn't change anything else, including how lines with missing fields are handled. Those still raise an error naming the line.