`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. I haven't run it on their actual file. The full test suite passes (19 tests, run with `python -m pytest`).

The fix is in `parse_entries` in `hourlog/importer.py`: lines that are empty or only whitespace are skipped. Line numbers in error messages still count the skipped lines, so a bad row after a blank one is reported at its real position in the file.

I added a test in `tests/test_importer.py` covering both cases: blank lines are skipped, and a later error still reports the right line number.

I left everything else in the importer alone. A line that is non-blank but malformed, such as one with a missing field, still raises an error.