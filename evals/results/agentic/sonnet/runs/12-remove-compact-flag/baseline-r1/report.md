I removed `--compact` / `-c`, and `cargo test` passes (14 unit tests and 12 integration tests). I didn't commit anything.

- **`src/cli.rs`:** I dropped the `compact` option, its parsing arm (including the deprecation warning) and its help line. `-c` and `--compact` now fail with the same "unknown option" error as any other unrecognised flag.
- **`src/render.rs`:** I removed the compact rendering path and its two unit tests.
- **Tests:**
  - The three old compact integration tests are replaced by one that checks both flags are rejected.
  - In `src/cli.rs`, the old unit test is now one that checks the flag is rejected.
- **Docs:** I removed the README table row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I didn't touch the version number in `Cargo.toml`, so the release bump to 1.0 is still yours to do.