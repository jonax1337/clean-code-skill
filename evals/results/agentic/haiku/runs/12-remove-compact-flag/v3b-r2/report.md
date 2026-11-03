I removed `--compact` (`-c`) and its code path. `cargo test` passes (13 unit tests and 11 integration tests), and the build has no warnings.

Changes:
- **`src/cli.rs`**: removed the flag from the help text, the `compact` field and its default, the parser arm that printed the deprecation warning, and its unit test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact` and its helper `trim_cells`, which nothing else used. Also removed their two unit tests.
- **`tests/cli.rs`**: removed the three compact integration tests.
- **`README.md`**: removed the `-c`, `--compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased, pointing to `--max-width`.

Behavior change: `-c` and `--compact` now fail with `unknown option`, the same as any other unrecognized flag. I didn't add a test that pins that rejection. The existing `rejects_unknown_options` test covers the general case.