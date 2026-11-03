`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer causes the error. All 19 tests pass, including the new one. I haven't run it on the accountant's actual file.

The importer in `hourlog/importer.py` tried to split every line into three fields. An empty line gave one field, which is the "expected 3, got 1" error. Lines that are only spaces or tabs are skipped too.

Line numbers in error messages still count the blank lines. If line 3 is bad and line 2 is empty, the error says "line 3", which matches what you'd see in a text editor.

I added a test for this in `tests/test_importer.py`. Malformed non-blank lines are still rejected as before.

I haven't committed anything.