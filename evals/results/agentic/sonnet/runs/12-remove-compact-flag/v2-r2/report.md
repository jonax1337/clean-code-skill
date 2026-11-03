I removed `--compact` / `-c`. `cargo test` passes (14 unit and 12 integration tests) with no warnings.

- **`src/cli.rs`:** I dropped the `compact` option, the flag parsing with its deprecation warning, and the usage line. `-c` and `--compact` now fail with the same unknown-option error as any other unrecognised flag.
- **`src/render.rs`:** I removed the compact rendering path and its two helper functions, along with their unit tests.
- **Tests:** I replaced the old compact tests with one unit test and one integration test. Both check that the flag is now rejected.
- **`README.md`:** I removed the option's row from the options table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased that points users to `--max-width`.

I didn't touch the version number, so bumping to 1.0 is still up to you.