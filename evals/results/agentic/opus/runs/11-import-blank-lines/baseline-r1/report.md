`hourlog import` no longer fails on the accountant's CSV: the importer now skips empty lines and lines containing only spaces. Before, it tried to split every line into three fields, so the empty last line caused the crash. The change is in `hourlog/importer.py`, in `parse_entries`. All 20 tests pass.

The skipped lines still count toward line numbers, so an error further down the file still points to the right line.

I added two tests to `tests/test_importer.py`: one checks that blank lines are skipped, and one checks that line numbers stay correct after a blank line. I haven't committed anything.