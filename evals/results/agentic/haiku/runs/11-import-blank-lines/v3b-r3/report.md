`hourlog import` now skips blank lines, so the trailing empty line in your accountant's file no longer causes the error.

The cause was in `hourlog/importer.py`: every line was split on commas, and a blank line produces a single field, so the unpack failed. The fix is a check in `parse_entries` that skips lines that are empty or whitespace-only. Line numbers still count them, so an error on a later line still reports the correct line in the file.

I added two tests to `tests/test_importer.py`: one covers blank lines in the middle and at the end of the input, and one checks that a bad line after a blank line still reports its real line number. `python -m pytest -q` gives 20 passed. I did not run the CLI against your accountant's actual file.

I haven't committed anything.