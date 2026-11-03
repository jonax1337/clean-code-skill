Blank lines in a CSV import are now skipped, so a trailing empty line no longer aborts `hourlog import`.

The cause was in `hourlog/importer.py`. An empty line splits into a single field, and `_parse_line` expected three. `parse_entries` now skips lines that are empty or whitespace-only. Line numbers still count every line, so a real error after a blank line is reported at its actual position.

I added two tests to `tests/test_importer.py`: one for blank lines being skipped, and one checking that a bad line after a blank line is still reported as the correct line number. The full suite passes: 20 tests, including the new ones.

I did not run the import against your accountant's actual file. If it fails again, send me the output and I'll look at it.