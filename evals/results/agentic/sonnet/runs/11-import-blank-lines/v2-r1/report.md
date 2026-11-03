`hourlog import` now skips blank lines, so the empty line 41 no longer stops the import. The full test suite passes (19 tests), including a new one for this case.

The cause was in `_parse_line` in `hourlog/importer.py`. It splits every line on commas, and an empty line splits into one empty value instead of the expected three. That produced "expected 3, got 1". The fix is in `parse_entries`, which now skips lines that are empty or only whitespace. Line numbers in error messages are unchanged, so a real error on a later line still reports the right line.

The new test, `test_import_ignores_blank_lines` in `tests/test_cli.py`, imports a file with blank lines in the middle and at the end.

I haven't run it against your accountant's actual file.