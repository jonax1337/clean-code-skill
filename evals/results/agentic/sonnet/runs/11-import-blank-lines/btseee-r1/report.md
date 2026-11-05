`hourlog import` now skips blank or whitespace-only lines, so the empty line 41 in your accountant's CSV no longer causes the error. All 20 tests pass. I didn't run it on the accountant's actual file.

The fix is in `hourlog/importer.py`, in `parse_entries`. The parser used to split every line into three fields, so an empty line gave "got 1".

Skipped lines still count toward line numbers, so an error on a real line still points at the right place in the file.

I added two tests in `tests/test_importer.py`: one for blank lines being skipped, and one for line numbers staying correct after a skipped line.

A line with some content but the wrong number of fields still fails, as before.