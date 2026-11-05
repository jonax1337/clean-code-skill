`hourlog import` now skips blank lines, including whitespace-only ones, so the empty line at the end of your accountant's CSV no longer causes an error. I haven't run it on the accountant's actual file. The full test suite passes (19 tests), including a new one for this case.

The fix is in `parse_entries` in `hourlog/importer.py`. Skipped lines still count toward line numbers, so an error on a later line still points at the right place in the file.

Lines that have content but the wrong number of fields still raise an error.