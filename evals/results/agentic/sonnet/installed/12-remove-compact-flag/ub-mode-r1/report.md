I removed `--compact` / `-c`, and `cargo test` passes with no warnings.

- **`src/cli.rs`:** I removed the usage line, the `compact` field on `Options`, the flag parsing (including the stderr deprecation warning) and the parser test.
- **`src/render.rs`:** I removed the compact branch, `render_compact`, `trim_cells` and the two compact unit tests.
- **`tests/cli.rs`:** I removed the three compact integration tests.
- **`README.md`:** I removed the option's table row.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased.

`-c` and `--compact` now fail with the existing unknown-option error.

I haven't committed anything.