`hourlog import` now skips blank lines, so the accountant's CSV should import. All 19 tests pass, including a new one for blank lines. I haven't run it on the accountant's actual file.

The parser split every line on commas and expected exactly three values. An empty line gave one value, which caused the unpack error. In `hourlog/importer.py`, `parse_entries` now skips lines that are empty or only whitespace. Line numbers in error messages still match the file, so a real error on line 12 will still say line 12.

I added `test_import_ignores_blank_lines` to `tests/test_cli.py`. It imports a file with a blank line in the middle and one at the end.

This skips blank lines anywhere in the file, not just at the end. I did that because accountant exports often have stray blank lines, and skipping them loses no data.