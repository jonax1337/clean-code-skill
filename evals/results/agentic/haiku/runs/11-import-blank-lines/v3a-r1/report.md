Blank lines in the import file no longer cause a crash. The full suite passes (19 tests, including a new one for this case).

**The cause:** `_parse_line` splits each line on commas and unpacks three values. A blank line gives a single empty string, so the unpack failed with that confusing message.

**The fix** is in `hourlog/importer.py`: `parse_entries` now skips lines that are empty or whitespace-only. Line numbers still count every physical line, so any real error after a blank line still points at the correct line in the accountant's file.

**The test** is `test_blank_lines_are_skipped_and_line_numbers_still_count_them` in `tests/test_importer.py`. It covers a blank line, a whitespace-only line with a CRLF ending, and a bad line after them that should be reported as line 4.

I haven't committed anything. I also haven't run `hourlog import` on the accountant's actual file, so it's worth one run to confirm.