`hourlog import` now skips blank lines, including lines that contain only whitespace, so the accountant's CSV with a trailing empty line imports normally. All 19 tests pass, including a new one for this case.

The fix is in `parse_entries` in `hourlog/importer.py`. Line numbers in error messages still match the file. The new test, `test_import_ignores_blank_lines`, is in `tests/test_cli.py`.

I didn't run the import on the accountant's actual file. Malformed lines still stop the import with an error naming the line, as the README describes.