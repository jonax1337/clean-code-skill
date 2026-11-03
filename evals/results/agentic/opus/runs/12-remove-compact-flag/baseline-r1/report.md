I've removed `--compact`. `cargo test` passes with no warnings: 13 unit tests and 12 integration tests.

**What changed:**
- **`src/cli.rs`**: removed the `-c`/`--compact` match arm and its deprecation warning, the `compact` field on `Options`, and its line in the help text.
- **`src/render.rs`**: removed the early return for compact mode, along with the `render_compact` and `trim_cells` functions that only it used.
- **`README.md`**: removed the `--compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased that points users to `--max-width`.

**Tests:** to keep the suite passing, I had to delete the six tests that checked how `--compact` behaved: three integration tests, two render unit tests and one cli unit test. Their behaviour no longer exists. I added one integration test, `removed_compact_flag_is_rejected`, which checks that `--compact` and `-c` now fail with `UnknownOption`.

This is a breaking change: scripts that still pass `-c` will now get an error instead of a warning. Nothing is committed yet.