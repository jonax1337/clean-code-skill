`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. The full test suite passes (20 tests). I haven't run the import on your accountant's actual file.

The importer in `hourlog/importer.py` tried to read every line as `date,project,minutes`, including empty ones. A line with no commas gave "expected 3, got 1". It now skips any line that is empty or only whitespace.

Skipped lines still count toward line numbers. If a real error comes after a blank line, the message points to the correct line in the file.

I added two tests in `tests/test_importer.py`: one for skipping blank and whitespace-only lines, and one for line numbers staying correct after a blank line.

Malformed non-blank lines, such as a line with a missing field, still raise an error.