I removed `--compact` / `-c`, and `cargo test` passes with no warnings (13 unit tests and 11 integration tests). I haven't committed anything.

- **`src/cli.rs`:** I removed the `compact` option field, the parsing branch that printed the deprecation warning, the help line, and the parser test. Passing `-c` or `--compact` now gives the normal unknown-option error.
- **`src/render.rs`:** I removed the compact branch, `render_compact`, `trim_cells`, and their two tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the option's row from the options table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased saying the flag is gone.

The tests that covered compact output went with the feature, so there are now fewer tests than before. I didn't add a test that `-c` is rejected, though the existing unknown-option test covers the same error path.