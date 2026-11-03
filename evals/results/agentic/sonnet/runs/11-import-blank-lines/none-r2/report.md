`hourlog import` now skips blank and whitespace-only lines, so the empty line at the end of your accountant's CSV no longer raises the error. I haven't run it on the accountant's actual file. The importer tests pass (8 passed), including a new one for this, and I didn't run the rest of the suite.

The fix is in `parse_entries` in `hourlog/importer.py`. It checks `line.strip()` and skips the line if it's empty. Skipped lines still count toward line numbers, so an error on a real line still points at the right place in the file.

I added `test_blank_lines_are_skipped_but_still_counted` to `tests/test_importer.py`.