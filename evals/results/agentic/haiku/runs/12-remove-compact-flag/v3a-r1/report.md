I removed `--compact` (and its short form `-c`) from the codebase. The tests pass: 13 unit and 11 integration, down from 16 and 14 because the compact-only tests were removed with the feature. `cargo test` shows no warnings.

Changes:
- **`src/cli.rs`**: removed the option from the help text, the `Options.compact` field and its default, the parser arm (which printed the deprecation warning), and its parser test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact` and `trim_cells`, and their two tests. `join_lines` stays because the normal render path uses it.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the `-c`/`--compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased. The 0.8.0 deprecation entry is kept as history.

After this change, `-c` and `--compact` fall through to the existing unknown-option error, the same as any unrecognized flag. I didn't add a separate message for them.

I haven't committed anything. Let me know if you want a commit.