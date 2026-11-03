I removed `--compact` / `-c`, and the tests pass. `cargo test` ran 26 tests (14 unit, 12 integration) with no failures, and `cargo clippy --all-targets` reported nothing.

- **Code:** I deleted the flag, its deprecation warning, the `compact` field on `Options`, the compact renderer and its helper (`src/cli.rs`, `src/render.rs`), and the help line.
- **Docs:** I removed the README row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.
- **Tests:** I deleted the tests that exercised compact output. I added two tests that `--compact` and `-c` now fail with `UnknownOption`: one in `src/cli.rs` and one in `tests/cli.rs`.

I didn't bump the version in `Cargo.toml`, since that's a release decision. The 0.8.0 changelog entry still mentions the deprecation, which is right for that release.