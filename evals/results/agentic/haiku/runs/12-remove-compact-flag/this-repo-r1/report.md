`--compact` (`-c`) is gone. The suite passes after the removal: 13 unit tests and 11 integration tests, down from 16 and 14 because I deleted the tests for the removed flag. `cargo test` showed no warnings, and `-c` now fails with `tabulate: unknown option `-c`` and exit code 2.

What changed:
- **`src/cli.rs`**: removed the `-c` help line, the `compact` field and its default, the parser arm with the deprecation warning, and the flag test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact`, `trim_cells` and their two tests.
- **`tests/cli.rs`**: removed the three compact tests.
- **`README.md`**: removed the `-c` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased. Since this changes behavior for anyone still passing `-c`, the entry matters.

I haven't committed anything. Let me know if you want a commit.