`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. All 20 tests pass, including the two new ones. I didn't run it on the accountant's actual file.

The parser was trying to split every line into `date,project,minutes`, and an empty line has no commas, which gave "expected 3, got 1". The fix is in `parse_entries` in `hourlog/importer.py`. Lines that are empty or only whitespace are skipped.

Skipped lines still count toward line numbers. If line 4 has a bad date, the error still says `line 4`, even when blank lines come before it.

I added two tests to `tests/test_importer.py`: one for a trailing blank line, and one for blank lines in the middle of a file with correct line numbers in the error.