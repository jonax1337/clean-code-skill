Fixed. `hourlog import` now skips blank lines, so a trailing empty line in the accountant's CSV no longer causes the error.

The cause was in `hourlog/importer.py`. `parse_entries` passed every line to `_parse_line`, and an empty line split on commas gives one value, so unpacking into three names failed. The loop now skips any line that is empty or only whitespace, before the line is parsed. Line numbers in other error messages still count the blank lines, so they still match the file.

I added `test_blank_lines_are_skipped` to `tests/test_importer.py`. It covers an empty line, a whitespace-only line with CRLF, and an empty string between valid rows. The full suite passes: 19 tests. I haven't run the import against the accountant's actual file. Nothing is committed.