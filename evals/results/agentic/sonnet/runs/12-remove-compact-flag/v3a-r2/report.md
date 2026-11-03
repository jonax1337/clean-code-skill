`--compact` and `-c` are gone, and `cargo test` passes: 14 unit tests and 12 integration tests, with no warnings or errors.

- **Code:** I removed the option from `src/cli.rs` (the `Options::compact` field, the parsing arm with its deprecation warning, and the help line). In `src/render.rs` I removed the compact branch, `render_compact` and `trim_cells`.
- **Tests:** I deleted the tests that exercised compact output. In their place are two tests that check `--compact` and `-c` are now rejected as unknown options.
- **Docs:** I removed the README table row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I didn't bump the version in `Cargo.toml`, so releasing 1.0 is still to do. Nothing is committed.