I removed `--compact` / `-c`, and `cargo test` passes. The integration suite runs 11 tests, and I only looked at the tail of the output, so I didn't confirm the unit-test count.

- **`src/cli.rs`:** I removed the `compact` option field, its default, the argument branch (which printed the deprecation warning), the help line, and the flag's unit test. `-c` and `--compact` are now rejected as `UnknownOption`, like any other unrecognised flag.
- **`src/render.rs`:** I removed the compact branch in `render_table`, plus `render_compact`, `trim_cells` and their two tests.
- **`tests/cli.rs`:** I removed the three compact tests.
- **`README.md`:** I removed the option's row from the table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased.

I didn't bump the version number. The changelog entry sits under Unreleased, so you can fold it into the 1.0 release notes when you cut it.