Fixed. `hourlog import` now skips empty lines, so the trailing blank line in your accountant's file no longer breaks the import.

**Change** (`hourlog/importer.py`): `parse_entries` skips any line that is empty or only whitespace, such as `"\n"`, `"  \r\n"` or a final empty line. This applies anywhere in the file, not only at the end. Line numbers still match the original file, so later errors point to the right line.

**Tests** (`tests/test_importer.py`): I added two tests. One checks that blank lines in the middle and at the end are skipped. The other checks that error messages still give the correct line number after a blank line. Both failed before the fix. After it, `pytest` passes all 20 tests.

**Not changed:** the importer splits each line on every comma. A project name with a comma in it, even in quotes (`"Acme, Inc."`), would still fail. A header row would fail too. I haven't seen your accountant's file, so I don't know whether either comes up. If they do, switching to Python's `csv` module would handle the quoting.