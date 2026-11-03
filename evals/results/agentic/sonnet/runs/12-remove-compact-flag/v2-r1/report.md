I removed `--compact` / `-c`. `cargo test` passes (13 unit tests, 11 integration tests) and `cargo clippy` is clean.

- **`src/cli.rs`:** I removed the flag parsing, the deprecation warning, the `compact` field on `Options`, the usage line, and the flag's unit test.
- **`src/render.rs`:** I removed the compact branch, its two helper functions (`render_compact` and `trim_cells`), and their tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the option row.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased that points to `--max-width`.

Passing `-c` or `--compact` now fails with `UnknownOption`, like any other unrecognized flag. I didn't bump the version in `Cargo.toml`, which is still 0.9.0, since you didn't ask for a release.