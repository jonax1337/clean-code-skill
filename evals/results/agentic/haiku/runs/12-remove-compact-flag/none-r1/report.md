`--compact` (`-c`) is removed. `cargo test` passes: 13 unit tests and 11 integration tests, with no failures.

Changes:
- **`src/cli.rs`**: removed the option, the `compact` field and its default, the parse arm with the deprecation warning, the help line, and the parser test.
- **`src/render.rs`**: removed the early return in `render_table`, `render_compact`, its helper `trim_cells`, and the two compact tests.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased. You didn't ask for this, so drop it if you'd rather handle the changelog differently.

Behaviour change: `-c` and `--compact` now fail with the usual unknown-option error, the same as any other unrecognised flag. Nothing is committed.