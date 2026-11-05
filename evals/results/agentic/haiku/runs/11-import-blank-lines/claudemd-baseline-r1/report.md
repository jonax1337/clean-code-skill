Fixed. `hourlog import` now skips blank lines, so a trailing empty line in the accountant's CSV no longer causes an error.

**The cause:** `parse_entries` in `hourlog/importer.py` tried to parse every line, including an empty one. An empty line splits into one field, so the three-way unpack failed.

**The change:**
- `hourlog/importer.py`: lines that are empty or whitespace-only are skipped. Line numbers still count them, so an error on a later line still points to the right line in the file.
- `tests/test_importer.py`: two new tests. One checks that blank lines between and after entries are skipped. The other checks that a bad line after a blank line is still reported with its real line number.

**Tests:** the full suite passes (`python -m pytest -q`, 20 passed). I didn't check that the new tests fail on the old code.

I haven't committed anything. Two things I didn't change: a line with only commas (like `,,`) still gives an error, and I didn't look at the `Entry` class to confirm that the "positive minutes" check the existing tests rely on is actually implemented.