I removed `--compact` (`-c`) completely. The suite passes: 13 unit tests and 11 integration tests, down from 16 and 14 because I deleted the tests for the removed flag. `cargo clippy --all-targets` is clean. Running `tabulate -c` now exits with `unknown option `-c``.

What changed:
- **`src/cli.rs`**: removed the option, its `Options.compact` field, its default, its help line, its deprecation warning, and its parser test.
- **`src/render.rs`**: removed the compact branch, `render_compact`, the `trim_cells` helper (used only by compact), and the two compact tests.
- **`tests/cli.rs`**: removed the three compact tests.
- **`README.md`**: removed the options table row.
- **`CHANGELOG.md`**: added a `### Removed` entry under Unreleased. The old 0.8.0 deprecation entry is untouched because it's history.

Nothing else in the repo referenced the flag. I didn't bump the version in `Cargo.toml`; that's up to you at release time.