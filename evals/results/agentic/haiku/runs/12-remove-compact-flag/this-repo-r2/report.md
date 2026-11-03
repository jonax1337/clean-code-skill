`--compact` (`-c`) is removed. The test suite passes: 13 unit tests and 12 integration tests, down from 16 and 14. The drop is the removed compact tests; I added one test that `--compact` is now rejected.

What changed:
- **`src/cli.rs`**: removed the option, its help line, the `compact` field and default, the parser arm with the deprecation warning, and its unit test.
- **`src/render.rs`**: removed the compact branch, `render_compact`, `trim_cells`, and their two tests.
- **`tests/cli.rs`**: replaced the three compact tests with `removed_compact_flag_is_rejected`, which checks that `--compact` returns `UnknownOption`.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased, pointing to `--max-width`.

Checks: `cargo test` ran clean with no warnings, and a grep finds no `compact` references left except the new test. I did not bump the version; it is still 0.9.0.

Scripts that pass `-c` will now fail with an unknown-option error instead of a deprecation warning. That is the intended breaking change, but it is worth a line in the release notes. Nothing is committed.