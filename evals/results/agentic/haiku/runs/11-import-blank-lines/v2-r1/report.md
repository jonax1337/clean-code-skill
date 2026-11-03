`hourlog import` now skips blank lines, so the trailing empty line in your accountant's CSV no longer causes the crash. The full test suite passes (19 tests).

The change is in `hourlog/importer.py`: `parse_entries` skips any line that is empty or only whitespace. Line numbers still count those lines, so an error on a later line still points to the right place in the file.

I also added `test_blank_lines_are_skipped` to `tests/test_importer.py`. It covers blank lines in the middle and at the end, with Windows line endings. I didn't run it against the unfixed code, but the old code fails on a blank line by design (`"".split(",")` gives one field), so it would have failed there too.

I haven't committed anything.