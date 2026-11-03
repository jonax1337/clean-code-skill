Fixed. `hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error.

The cause was in `hourlog/importer.py`: `_parse_line` splits each line on commas and expects three values. An empty line splits into one value, which is what produced "expected 3, got 1". The fix is in `parse_entries`: any line that is empty or only whitespace is skipped before parsing.

I added `test_blank_lines_are_skipped` to `tests/test_importer.py`. It covers blank lines in the middle of the file as well as at the end, including a whitespace-only line with `\r\n`. The full suite passes (19 tests).

I haven't run it against the accountant's actual file. Lines with the wrong number of fields still raise an error naming the line, as before.