`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. I didn't run it on the accountant's actual file.

The parser in `hourlog/importer.py` split every line on commas, including empty ones. An empty line gave one value instead of three, which is the "expected 3, got 1" error. It now skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers, so a bad row after a blank line is reported at its real position in the file.

I added `test_blank_lines_are_skipped_but_still_counted` to `tests/test_importer.py`. I ran `python -m pytest -q` after the change and all 19 tests pass. I didn't run the new test against the old code to confirm it fails there.

I didn't change anything else. A line that has text but the wrong number of fields still raises an error.