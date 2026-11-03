`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. I ran the test suite and all 19 tests pass. I didn't run the import on the accountant's actual file.

The importer in `hourlog/importer.py` tried to read every line as `date,project,minutes`. An empty line split into one value, which caused the "expected 3, got 1" message. A line containing only whitespace is skipped the same way.

Line numbers in error messages still count the skipped lines. A malformed row on line 41 is still reported as line 41, so it matches what you see in a spreadsheet or editor.

I added a test for this in `tests/test_importer.py`. It covers blank lines in the middle and at the end of the data, and checks that the line numbers stay correct. I didn't confirm that the new test fails without the fix.