Fixed. `hourlog import` now skips blank and whitespace-only lines, so the trailing empty line in your accountant's CSV no longer stops the import. The full test suite passes (20 tests, including 2 new ones).

**The cause:** `_parse_line` split every line on commas, and an empty line splits into a single field, which failed the three-way unpack.

**The change:**
- `hourlog/importer.py`: `parse_entries` skips any line where `line.strip()` is empty. Line numbers still come from `enumerate` over the file, so a later bad line is still reported with its real line number.
- `tests/test_importer.py`: added two tests:
  - blank lines (including CRLF and whitespace-only lines) are skipped and produce no entries;
  - a bad line after a blank line reports its actual line number.

**One choice to be aware of:** blank lines are now silently ignored, which goes slightly beyond the README's "one entry per line" wording. I think that's the right behavior for a trailing newline or spacer lines, but if you'd rather keep blank lines as errors, let me know and I'll change it.

I didn't commit anything. Let me know if you want me to commit this or open a PR.