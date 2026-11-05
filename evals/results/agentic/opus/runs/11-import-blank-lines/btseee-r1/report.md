`hourlog import` now skips blank lines, so the empty line at the end of your accountant's CSV no longer breaks it. The full test suite passes (20 tests).

**The cause:** `parse_entries` in `hourlog/importer.py` passed every line to the parser, including empty ones. An empty line can't be split into date, project and minutes, which produced that error.

**The fix:** two lines in `hourlog/importer.py` that skip any line that is empty or contains only spaces. This applies anywhere in the file, not just at the end. Error messages still report the real line number from the file.

**Tests:** I added two to `tests/test_importer.py`. One checks that blank lines are skipped, including ones with Windows line endings. The other checks that line numbers in error messages still count the skipped lines. Both failed before the fix and pass now.

I haven't run it against your accountant's actual file, so it's worth trying the import again with it. Nothing is committed.