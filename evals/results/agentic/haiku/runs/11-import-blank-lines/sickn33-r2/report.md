Fixed: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer raises an error.

The cause was in `hourlog/importer.py`. `parse_entries` passed every line to `_parse_line`, and an empty line split on commas gives one value, not the three it expects. The fix is a check in `parse_entries` that skips lines that are empty or whitespace-only. Line numbers still count skipped lines, so an error on a later line still points at the right line in the file.

I added two tests to `tests/test_importer.py`:
- Blank lines in the middle and at the end are skipped, including `\r\n` and whitespace-only lines.
- A bad row after a blank line is reported with its actual line number.

The full suite passes (20 tests). I haven't run it against the real file from your accountant. Running `hourlog import` on it would confirm the fix there.