Fixed. `hourlog import` now skips blank lines, so the empty line at the end of the accountant's file no longer causes the error.

**Cause:** `_parse_line` splits every line on commas and unpacks three values. A blank line splits into one value, which produced the "expected 3, got 1" message.

**Change:** In `hourlog/importer.py`, `parse_entries` now skips any line that is empty or whitespace-only. Line numbers still count skipped lines, so an error on a later line still reports the correct line in the file.

**Tests:** I added two tests to `tests/test_importer.py`:
- Blank lines between and after entries are skipped, including `\r\n` endings.
- A bad row after a blank line is reported with its real file line number.

The full suite passes: 20 passed.

I didn't have the accountant's file, so I haven't run it against the real export. I also haven't committed anything.