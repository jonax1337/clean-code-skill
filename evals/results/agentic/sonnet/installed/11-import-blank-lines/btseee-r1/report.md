`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. The full test suite passes (19 tests), including a new one for this case.

The parser in `hourlog/importer.py` tried to split every line into three values, and an empty line gave it only one. It now ignores any line that is empty or only whitespace. Line numbers in error messages still count the skipped lines, so a bad row is reported at its real position in the file.

I haven't run the import against your accountant's actual file, only the tests.

The new test is `test_blank_lines_are_skipped_but_still_counted` in `tests/test_importer.py`.