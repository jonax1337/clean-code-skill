I removed `--compact` / `-c` and everything that supported it. `cargo test` passes (13 unit tests, 11 integration tests) with no warnings. I haven't committed anything.

- **`src/cli.rs`:** I removed the flag, the `compact` field on `Options`, the deprecation warning, the line in the usage text, and its parser test.
- **`src/render.rs`:** I removed `render_compact`, `trim_cells`, the early return in `render_table`, and the two compact tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the options table row.
- **`CHANGELOG.md`:** I added a `Removed` entry under Unreleased, pointing people to `--max-width`.

After this change, `-c` and `--compact` fail with the existing "unknown option" error.