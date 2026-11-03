I removed `--compact` / `-c`. All tests pass (14 unit, 12 integration), and clippy is clean.

- **`src/cli.rs`:** I took out the `compact` option field, its parsing branch (which printed the deprecation warning) and its help line. `-c` and `--compact` now fail with `UnknownOption`, like any other unknown flag.
- **`src/render.rs`:** I removed the compact rendering path, its two helper functions and their two unit tests.
- **`tests/cli.rs`:** I replaced the three compact tests with one that checks `--compact` is rejected. The same check for `-c` and `--compact` is in the `src/cli.rs` unit tests.
- **Docs:** I deleted the README table row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

The crate version is still 0.9.0. I didn't bump it to 1.0, so that's still to do when you release.

I haven't committed anything.