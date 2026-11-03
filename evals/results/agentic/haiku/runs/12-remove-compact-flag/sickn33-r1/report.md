I removed `--compact` (and its short form `-c`) from the code, tests, README and changelog. `cargo test` passes: 13 unit tests and 11 integration tests, with no failures. Clippy is clean, and no `compact` references remain in `src`, `tests` or the README.

Changes:
- **`src/cli.rs`**: removed the `compact` field and its default, the `-c`/`--compact` parse arm with its deprecation warning, the help line, and the `compact_flag_sets_compact` test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact`, `trim_cells` and the two compact tests. `join_lines` stays, since the normal path still uses it.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the `-c` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased.

Behaviour change: `-c` and `--compact` now fail with `UnknownOption`, like any other unrecognised flag. Nothing in the repo expected a different result from them, so the tests don't cover that case.

Nothing is committed yet. Say if you want a commit on `main` or a branch.