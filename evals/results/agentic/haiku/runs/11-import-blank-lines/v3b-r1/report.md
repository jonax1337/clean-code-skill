Blank lines in the import file are now skipped, so your accountant's CSV should import.

The cause was in `hourlog/importer.py`: an empty line splits into a single field, so unpacking into `day, project, minutes` failed. The parser now skips any line that is empty or only whitespace before parsing it. Real errors on other lines still report their line number, because the numbering counts every line in the file.

I added `test_blank_lines_are_skipped` in `tests/test_importer.py`, covering blank, whitespace-only and CRLF-blank lines between entries. `python -m pytest -q` passes: 19 passed. I did not run the new test against the old code to watch it fail; by reading the code, the old code would raise on the blank line.

I haven't run the import against your accountant's actual file. Nothing is committed.