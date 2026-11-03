`hourlog import` now skips blank lines, including whitespace-only ones, so the empty line at the end of your accountant's CSV no longer causes the error. The full test suite passes (20 tests).

The fix is in `parse_entries` in `hourlog/importer.py`. Line numbers in error messages still count the blank lines, so a real error is reported at the line number you'd see in a text editor.

I added two tests in `tests/test_importer.py`. One checks that blank lines are skipped. The other checks that error line numbers still count them. I haven't run the import on your accountant's actual file.