`hourlog import` now skips blank lines, so the empty last line of your accountant's CSV no longer causes the error. The full suite passes (19 tests, including a new one).

The cause was in `hourlog/importer.py`. An empty line splits into a single field, so the three-way unpack in `_parse_line` failed. `parse_entries` now skips any line that is empty or only whitespace before parsing it. Lines with real content are still checked as before, so a malformed line still fails with its line number.

I added `test_blank_lines_are_skipped` in `tests/test_importer.py`. It covers an empty line, a whitespace-only line with CRLF, and a trailing empty string.

I haven't run the import against the accountant's actual file. Changes are uncommitted in the working tree.