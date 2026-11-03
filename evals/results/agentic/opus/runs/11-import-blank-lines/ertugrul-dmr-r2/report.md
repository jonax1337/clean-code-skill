I fixed it: `hourlog import` now skips empty lines instead of failing on them. All 21 tests pass, including three new ones.

**Cause:** `_parse_line` split every line on commas and expected three fields. The empty last line had only one field, so it failed.

**Fix** (`hourlog/importer.py`): `parse_entries` now skips any line that is empty or contains only spaces, tabs or a line break. I put that check in a small `_is_blank` function so the loop reads clearly.

This also skips blank lines in the middle of a file, not just at the end. I think that's the right behaviour for an export, but tell me if you'd rather blank lines in the middle still be reported as errors.

Error messages still give the real line number in the file, even when blank lines have been skipped before it.

**New tests** (`tests/test_importer.py`):
- An empty line at the end is ignored (your accountant's case).
- Lines containing only spaces, tabs or a Windows line ending are ignored anywhere in the file.
- An error after a skipped blank line still reports the correct line number.