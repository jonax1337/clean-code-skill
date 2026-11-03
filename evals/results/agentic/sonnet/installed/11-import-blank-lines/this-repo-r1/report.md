`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. `pytest` passes: 20 passed. I didn't run `hourlog import` on the accountant's actual file.

The fix is in `hourlog/importer.py`. `parse_entries` skips any line that is empty or only whitespace. Line numbers in error messages still count the blank lines. A bad row on line 3 is still reported as "line 3", even if line 2 was blank.

I added two tests in `tests/test_importer.py`: one that blank lines are skipped, and one that line numbers count them. I didn't run the blank-line test against the old code, so I haven't seen it fail without the fix.

Rows that have some content but the wrong number of fields, like a stray `foo`, still raise an error.

I haven't committed anything.