Fixed. `hourlog import` now skips blank lines, so the accountant's trailing empty line no longer crashes the import.

**Cause:** `parse_entries` passed every line to `_parse_line`, including empty ones. `"".split(",")` returns one value, so unpacking into `day, project, minutes` failed.

**Change** (`hourlog/importer.py`): lines that are empty or whitespace-only are skipped. Line numbers still count physical lines, so a genuinely bad line later in the file is still reported at its real position.

**Tests** (`tests/test_importer.py`): added two tests:
- blank lines (including `\r\n` and whitespace-only ones) are skipped and the entries around them are parsed
- a bad line after blank lines reports its physical line number

The full suite passes: 20 tests, including the two new ones. I didn't run the import against the accountant's actual file.