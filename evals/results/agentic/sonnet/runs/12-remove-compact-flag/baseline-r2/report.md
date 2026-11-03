I removed `--compact` / `-c`, and all tests pass with no compiler warnings (13 unit tests and 11 CLI tests).

- **`src/cli.rs`**: removed the help line, the `compact` field and its default, the arg-parsing arm (which printed the deprecation warning), and the `compact_flag_sets_compact` test.
- **`src/render.rs`**: removed the compact branch, `render_compact`, `trim_cells`, and the two compact tests.
- **`tests/cli.rs`**: removed the three compact tests.
- **`README.md`**: removed the options table row.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased.

`--compact` and `-c` now fall through to the existing unknown-option error. I didn't add a test for that, since `--nope` already covers that path.

I haven't committed anything.