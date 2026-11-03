I've removed `--compact`. All tests pass: 13 unit tests and 12 integration tests, with no compiler warnings.

**What changed**
- **`src/cli.rs`**: `-c`/`--compact` is gone from the help text, from the argument parser (along with its deprecation warning) and from `Options`. Both spellings now fail with an "unknown option" error.
- **`src/render.rs`**: the compact output path and its two helper functions are gone.
- **`README.md`**: the `--compact` row is gone from the options table.
- **`CHANGELOG.md`**: there's a new "Removed" entry under Unreleased that points users to `--max-width`. I left the 0.8.0 deprecation note in place, since it's history.

**Tests:** Six tests checked the old compact behaviour, so they couldn't pass once the flag was gone. I deleted them: one in `src/cli.rs`, two in `src/render.rs` and three in `tests/cli.rs`. In their place I added `removed_compact_flag_is_rejected` to `tests/cli.rs`, which checks that `--compact` and `-c` are both rejected. That gives a clear error for anyone whose scripts still pass the flag.

Nothing is committed yet.