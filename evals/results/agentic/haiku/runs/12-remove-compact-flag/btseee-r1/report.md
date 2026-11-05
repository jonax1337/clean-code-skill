I removed `--compact` (`-c`) and all its code. The full test suite passes: 13 unit tests and 12 integration tests, with no leftover references outside the changelog history.

Changes:
- **`src/cli.rs`**: removed the option from the usage text, the `Options` struct and its default, the parser arm (which printed the deprecation warning), and its unit test.
- **`src/render.rs`**: removed the compact branch in `render_table`, plus `render_compact` and its helper `trim_cells`, and the two compact tests.
- **`tests/cli.rs`**: replaced the three compact tests with one test asserting that `--compact` now fails with `UnknownOption`. That pins the removal, since the flag is now an unknown option.
- **`README.md`**: removed the `-c, --compact` row from the options table.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased, noting it was deprecated in 0.8.0 and that `--max-width` replaces it.

Decisions for you to check:
- I kept the `CHANGELOG.md` 0.8.0 entry as history rather than editing it.
- `-c` is now rejected like any unknown option, with no special message. If you want a friendlier error for people upgrading from 0.8, that would be a small addition.

I haven't committed anything.