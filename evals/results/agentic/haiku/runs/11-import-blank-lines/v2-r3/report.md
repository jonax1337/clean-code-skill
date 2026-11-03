`hourlog import` now skips blank lines, so a trailing empty line in the accountant's CSV no longer causes the error. All 20 tests pass, including two new ones I added.

**The cause:** `_parse_line` expects exactly three comma-separated fields. An empty line splits into a single empty field, so the unpack failed.

**The fix** (`hourlog/importer.py`): `parse_entries` skips any line that is empty or whitespace-only. Line numbers still count skipped lines, so a real error later in the file still reports the correct line.

**Tests** (`tests/test_importer.py`):
- `test_blank_lines_are_skipped` covers empty, whitespace-only, and CRLF blank lines mixed with valid rows.
- `test_bad_line_after_blank_lines_keeps_its_line_number` checks that an error after a blank line is still reported as line 3.

I did not commit anything. I also did not run the CLI against your accountant's actual file, so if the import still fails, the error text will show what else is in it. One thing to watch for: if the file was saved from Excel with a UTF-8 BOM, the first date will fail to parse. The importer opens files as plain `utf-8`, so I left that alone.