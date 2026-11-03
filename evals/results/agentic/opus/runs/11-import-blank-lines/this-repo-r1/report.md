I fixed it: `hourlog import` now skips blank lines, so the accountant's file should import.

**The cause:** `parse_entries` in `hourlog/importer.py` split every line into three fields, including empty ones. An empty line gives only one field, which is why line 41 failed.

**The change:**
- `hourlog/importer.py`: lines that are empty or contain only spaces are skipped, whether they're at the end or in the middle of the file. Line numbers still count them, so an error message points to the right line in the file.
- `tests/test_importer.py`: two new tests. One checks that blank lines (including `" \r\n"`) are skipped. The other checks that an error after a skipped blank line still reports the correct line number.
- `README.md`: the CSV section now says blank lines are skipped.

**Tests:** `python -m pytest` gives 20 passed. With the fix removed, the new tests fail (2 failed, 7 passed in `test_importer.py`). I didn't run it against the accountant's actual file, since I don't have it.

My first attempt edited the files with a script, which broke a string in the test file and made Python unable to load it. I reverted those edits with `git checkout` and made them again directly. Nothing from that attempt remains. The changes are uncommitted.