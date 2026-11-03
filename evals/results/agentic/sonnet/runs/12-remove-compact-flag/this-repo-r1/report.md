`--compact` and `-c` are gone, and `cargo test` passes (14 unit tests and 12 integration tests). `cargo clippy --all-targets` printed no warnings.

- **Code:** In `src/cli.rs` I removed the `compact` field, its default, the flag parsing (including the deprecation warning) and the help line. In `src/render.rs` I removed the compact branch and its two helper functions.
- **Docs:** I deleted the README option row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.
- **Tests:** I deleted the tests that exercised compact output. I added two tests that `--compact` and `-c` are now rejected as unknown options, one in `src/cli.rs` and one in `tests/cli.rs`.

I did not touch the version number in `Cargo.toml`, which is still 0.9.0, so bumping to 1.0 is up to you.