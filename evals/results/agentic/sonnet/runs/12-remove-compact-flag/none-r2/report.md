`--compact` (`-c`) is gone, and `cargo test` passes with no warnings (13 unit tests, 11 integration tests).

- **`src/cli.rs`:** I removed the flag parsing, the deprecation warning, the `compact` field on `Options`, the help line, and the flag's unit test.
- **`src/render.rs`:** I removed the compact branch, `render_compact`, `trim_cells`, and the two compact tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the option's row from the options table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased.

Passing `-c` or `--compact` now fails with the usual unknown-option error. I haven't committed anything.