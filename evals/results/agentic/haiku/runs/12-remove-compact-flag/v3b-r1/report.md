`--compact` is removed. `cargo test` passes: 13 unit tests and 11 integration tests, down from 14 integration tests before the change. The 3 removed integration tests were the compact ones, and the 3 removed unit tests were compact tests in `src/cli.rs` and `src/render.rs`. `cargo clippy --all-targets` is clean, and `grep` finds no remaining references to `compact` in `src`, `tests`, or `README.md`.

**What changed**
- `src/cli.rs`: removed the `compact` field and its default, the `-c`/`--compact` arm with its deprecation warning, the usage line, and the flag's unit test.
- `src/render.rs`: removed the compact branch in `render_table`, plus `render_compact` and `trim_cells`, and the two compact tests.
- `tests/cli.rs`: removed the three compact integration tests.
- `README.md`: removed the `-c`/`--compact` row from the options table.
- `CHANGELOG.md`: added a "Removed" entry under Unreleased. I left the 0.8.0 deprecation entry as history.

**Behavior change:** `-c` and `--compact` now fail with `tabulate: unknown option`, exit code 2. I checked this with a run of `-c`. Scripts that still pass `-c` will break, which is the point of the removal.

**Not done:** I did not commit. I also did not add a test that pins `-c` as rejected. The existing `rejects_unknown_options` test covers the general case.