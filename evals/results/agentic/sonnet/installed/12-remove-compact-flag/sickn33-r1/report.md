I removed `--compact` / `-c`, and `cargo test` passes with no warnings.

- **`src/cli.rs`:** I dropped the `compact` option, the flag parsing (including the deprecation warning), the help line, and the parser test for it. Passing `-c` or `--compact` now gives the usual "unknown option" error.
- **`src/render.rs`:** I removed `render_compact`, `trim_cells`, the early return that used them, and their two unit tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the flag's row from the options table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased. It says the flag was deprecated since 0.8 and points to `--max-width`.

I haven't bumped the version to 1.0 or committed anything.