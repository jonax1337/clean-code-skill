`hourlog import` now skips blank lines, so the empty line 41 in your accountant's CSV no longer raises the error. I haven't run it on the actual CSV file. The full suite passes (19 tests), including a new importer test for this.

Blank means empty or whitespace-only. Error messages still count those lines, so a real error is reported at its true line number in the file.

**Log**
- I read `hourlog/importer.py` and found the cause: `_parse_line` split every line on commas, including empty ones.
- I added a test in `tests/test_importer.py` and ran it. It failed with the same "not enough values" error before the fix.
- I added a `continue` in `parse_entries` for blank lines (`hourlog/importer.py`).
- I ran the full suite and committed the change as `e971fe7` on `main`. I did not push it, and I didn't run the crapper, dryer or mutator tools.