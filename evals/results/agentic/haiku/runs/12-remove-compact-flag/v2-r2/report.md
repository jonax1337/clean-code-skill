`--compact` is gone, and the test suite passes.

**What I removed**
- `src/cli.rs`: the `-c, --compact` usage line, the `compact` field and its default, the parser arm that printed the deprecation warning, and the `compact_flag_sets_compact` unit test.
- `src/render.rs`: the early-return compact branch in `render_table`, plus `render_compact` and `trim_cells`, which only the compact path used. Also the two compact unit tests.
- `tests/cli.rs`: the three compact integration tests.
- `README.md`: the `-c, --compact` row in the options table.

**What I added**
- `CHANGELOG.md`: a `### Removed` entry under Unreleased, pointing users to `--max-width`. I left the 0.8.0 deprecation entry as history.

**Verification**
- `cargo test`: 13 unit tests and 11 integration tests pass, with no compile warnings.
- `git grep` finds no remaining `compact` references outside the CHANGELOG.

**Behavior change:** `-c` and `--compact` now fail with `UnknownOption` instead of printing a warning and running. I did not bump the version. I also did not commit; the changes are in the working tree.