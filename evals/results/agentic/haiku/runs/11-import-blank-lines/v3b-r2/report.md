`hourlog import` now skips blank lines, so the trailing empty line in your accountant's file no longer causes the unpack error.

The cause was in `hourlog/importer.py`: an empty line became `""` after stripping the newline, and `split(",")` returned one value where the parser expected three. The fix is a check in `parse_entries` that skips any line that is blank after stripping whitespace. Line numbers still count skipped lines, so errors on later lines still point at the correct line in the file.

I added `test_blank_lines_are_skipped` to `tests/test_importer.py`, covering a blank line, a whitespace-and-CRLF line, and a trailing blank line. Running `python -m pytest -q` gives 19 passed. I did not run the new test against the unfixed code to confirm it fails there. Based on the trace above it should, but I haven't checked it.

I did not run the command on the accountant's actual file, so it's worth one import of that file to confirm.