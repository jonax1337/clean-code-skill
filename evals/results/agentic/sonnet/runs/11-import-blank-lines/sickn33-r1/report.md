`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. The full test suite passes (19 tests), including a new one for this case.

The cause was in `parse_entries` in `hourlog/importer.py`. It tried to split every line into `date,project,minutes`, and an empty line has no commas. A line with only spaces is skipped too. Line numbers in error messages still count the blank lines, so an error on a real line still points at the right place.

The new test is `test_import_ignores_blank_lines` in `tests/test_cli.py`. It imports a file with blank and whitespace-only lines in the middle and at the end.

I haven't committed anything.