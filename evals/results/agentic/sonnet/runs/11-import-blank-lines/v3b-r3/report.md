`hourlog import` now skips blank and whitespace-only lines, so the empty line at the end of your accountant's CSV no longer causes an error. I didn't have the actual file, so I tested with a made-up one. The full suite passes (`python -m pytest -q`: 19 passed).

The cause was in `hourlog/importer.py`. `parse_entries` tried to split every line into `date,project,minutes`, and an empty line splits into one value instead of three. I added a check in `parse_entries` that skips lines with nothing but whitespace.

Skipped lines still count toward line numbers, so an error on a real line still points at the right place in the file. I added a test in `tests/test_importer.py` covering both the skipping and the line numbers. I didn't confirm it fails without the fix.

Lines that are malformed but not blank, such as a stray header row, still raise an error.

I haven't committed anything.