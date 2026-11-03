Fixed. Blank lines in the import file are now skipped, so the trailing empty line from your accountant's CSV no longer breaks `hourlog import`.

The cause was in `hourlog/importer.py`. `parse_entries` passed every line to `_parse_line`, which splits on commas. An empty line splits into one field, so unpacking into `day, project, minutes` failed. The line number was correct, but the line was blank.

Changes:
- **`hourlog/importer.py`**: `parse_entries` skips any line that is empty or only whitespace. Lines with bad data still raise `ImportFormatError` with their line number.
- **`tests/test_importer.py`**: added `test_blank_lines_are_skipped`, which covers blank lines in the middle and at the end, including `\r\n` endings.

The full suite passes (19 tests). I didn't run the CLI against your accountant's actual file, so it's worth one `python -m hourlog import` run on it to confirm. I haven't committed anything.