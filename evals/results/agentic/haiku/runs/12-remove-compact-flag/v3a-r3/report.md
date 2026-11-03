`--compact` / `-c` is removed. The tests pass: 13 unit and 12 integration, down from 16 and 14 because I deleted the tests for the removed flag. The build has no warnings.

**Changes**
- `src/cli.rs`: removed the `compact` field, its default, the `-c`/`--compact` parser arm (which printed the deprecation warning), the help line, and its unit test.
- `src/render.rs`: removed the compact branch in `render_table`, plus `render_compact` and `trim_cells`, which only it used. `join_lines` stays because the normal path uses it. Removed its two tests.
- `tests/cli.rs`: removed the three compact tests and added `removed_compact_flag_is_rejected`, which checks that `--compact` now returns `UnknownOption`.
- `README.md`: removed the options-table row.
- `CHANGELOG.md`: added a `### Removed` entry under Unreleased. The 0.8.0 deprecation entry stays as history.

**Decisions for you to check**
- The removed flag now fails as an unknown option, not with a special message. A user who still passes `-c` gets `unknown option` and no hint. If you want a friendlier error, that's a small follow-up.
- Removing the flag breaks anyone who still passes `-c`. The CHANGELOG entry says so, but I did not bump the version. That's your call.

I did not commit. The only remaining "compact" references are the two CHANGELOG entries.