I removed `--compact` / `-c`, and the integration tests pass (12 passed). I only saw the tail of the `cargo test` output, so I didn't see the unit-test results for `src/cli.rs` and `src/render.rs`. The compile and `cargo clippy --all-targets` runs were clean.

- **Code:** `src/cli.rs` loses the `compact` option, the flag parsing with its stderr warning, and the usage line. `src/render.rs` loses `render_compact` and `trim_cells`.
- **Behavior:** `--compact` and `-c` now fail with `UnknownOption` like any other unknown flag.
- **Tests:** I deleted the tests for compact rendering. I added tests that `--compact` and `-c` are rejected, one in `src/cli.rs` and one in `tests/cli.rs`.
- **Docs:** I removed the README option row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

`cargo fmt --check` reports formatting differences in `src/render.rs`. They are in lines I didn't touch (the `Options { border: true, ... }` test lines), so I left them alone. I didn't bump the version number to 1.0.