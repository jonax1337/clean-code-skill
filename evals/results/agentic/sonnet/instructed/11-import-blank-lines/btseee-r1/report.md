`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. The full suite passes (19 tests), including the new one.

The importer was splitting every line into `date,project,minutes`. An empty line has no commas, which is why you saw "expected 3, got 1". I added a check in `parse_entries` in `hourlog/importer.py` that skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers. If a later line is malformed, the error still points at the right line in the file.

I wrote the new test in `tests/test_importer.py` alongside the fix, but I didn't run it against the old code first, so I haven't seen it fail.

I haven't run the import on the accountant's actual file.