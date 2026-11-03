I fixed the import so it skips blank lines. Your accountant's CSV should now import, and all 20 tests pass. I haven't run it on their actual file.

The parser in `hourlog/importer.py` tried to split every line into `date,project,minutes`. An empty line gave one value instead of three, which is the "expected 3, got 1" error. `parse_entries` now skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers. If a later line is malformed, the error points at the right line in the file.

I added two tests in `tests/test_importer.py`. One checks that blank lines are skipped, and the other checks that error line numbers stay correct after a blank line.