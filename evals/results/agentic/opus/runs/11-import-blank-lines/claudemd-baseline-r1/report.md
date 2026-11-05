I fixed it: `hourlog import` now skips blank lines, so the empty line at the end of your accountant's file no longer causes an error.

**What was wrong:** The importer in `hourlog/importer.py` split every line on commas and expected three values. An empty line gives only one value, so it crashed.

**The fix:** In `parse_entries`, lines that are empty or contain only spaces are now skipped before parsing. Line numbers are still counted the same way, so errors on later lines report the correct line number.

One thing to know: blank lines are now skipped anywhere in the file, not just at the end. I think that's the sensible behaviour since an empty line holds no entry, but if you'd rather have blank lines in the middle of a file reported as errors, that's an easy change.

**Tests:** I added two tests to `tests/test_importer.py`. One checks that a trailing empty line is ignored. The other has a blank line with spaces and a Windows line ending (`"  \r\n"`) in the middle of the file, and checks that an error after it still names the right line. All 20 tests pass. I didn't run it on the accountant's actual file because I don't have it, so a quick `hourlog import` on that file would confirm the fix.