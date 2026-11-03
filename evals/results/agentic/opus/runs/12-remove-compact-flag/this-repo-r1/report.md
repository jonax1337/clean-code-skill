I've removed `--compact`. The tests pass, but I had to delete six tests that checked the compact output, so the suite is now smaller.

**What changed**
- `src/cli.rs`: removed the `-c`/`--compact` match arm and its deprecation warning, the line in the help text, and the `compact` field on `Options`.
- `src/render.rs`: removed the compact branch in `render_table` and the two functions only it used, `render_compact` and `trim_cells`.
- `README.md`: removed the option's row from the table.
- `CHANGELOG.md`: added a "Removed" entry under Unreleased.

**Tests:** I deleted the six tests that checked compact output: two in `render.rs`, one in `cli.rs` and three in `tests/cli.rs`. In their place, `tests/cli.rs` now has `removed_compact_flag_is_rejected`, which checks that both `--compact` and `-c` give an `UnknownOption` error. Anyone still passing the flag gets that error rather than a quiet change in output.

**Checks run**
- `cargo test`: 13 unit tests and 12 integration tests passed, none failed.
- `cargo clippy --all-targets`: no warnings.
- Searching `src`, `tests` and the README for "compact" now only finds the new test.

**One thing to know:** `compact` was a `pub` field on the public `Options` struct. Any library user who set it will get a compile error. That fits a 1.0 breaking change, but it should be mentioned in the release notes.