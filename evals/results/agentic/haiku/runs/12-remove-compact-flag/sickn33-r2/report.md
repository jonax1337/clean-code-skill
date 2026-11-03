`--compact` / `-c` is gone. `cargo test` passes: 13 unit tests and 12 integration tests, with no build warnings shown.

What changed:
- **`src/cli.rs`**: removed the flag, the `compact` field, its default, the deprecation warning, the help line, and the flag test.
- **`src/render.rs`**: removed the compact branch, `render_compact`, the helper `trim_cells` that only it used, and its two tests.
- **`tests/cli.rs`**: replaced the three compact tests with one test asserting that `--compact` and `-c` now fail with `UnknownOption`. This is the one addition beyond pure deletion; it keeps the removal covered by a test.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased, noting it was announced in 0.8.0 and pointing to `--max-width`.

I did not commit anything. A grep afterwards finds no remaining compact references apart from the new rejection test.