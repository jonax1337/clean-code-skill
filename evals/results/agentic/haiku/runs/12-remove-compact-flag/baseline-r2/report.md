`--compact` / `-c` is removed, and `cargo test` passes (13 unit tests and 11 integration tests) with no build warnings.

What changed:
- **`src/cli.rs`**: dropped the `compact` field, its parse arm (with the deprecation warning), the usage line, and its unit test.
- **`src/render.rs`**: dropped the compact branch in `render_table`, plus `render_compact` and `trim_cells`, which only the compact path used. Their two tests are gone too.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the option row.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased. The 0.8.0 deprecation entry stays as history.

One behavior change to be aware of: `-c` and `--compact` now fail with the unknown-option error instead of printing a warning and working. Anyone still passing the flag in scripts will break, which is what the 1.0 deprecation promised. The CHANGELOG entry says so. I didn't commit anything.