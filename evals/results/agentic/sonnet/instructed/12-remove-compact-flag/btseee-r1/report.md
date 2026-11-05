`--compact` and `-c` are removed, and `cargo test` passes with no warnings: 14 unit tests and 12 integration tests.

- **Code:** I deleted the flag parsing and its deprecation warning, the `compact` option, the compact render path, and the usage line in `src/cli.rs` and `src/render.rs`.
- **Docs:** The README option row is gone, and `CHANGELOG.md` has a new "Removed" entry under Unreleased.
- **Tests:** I removed the tests that covered compact output, because the feature no longer exists. In their place, one unit test and one integration test check that `--compact` and `-c` are now rejected as unknown options.

Anyone who still passes `-c` will now get an "unknown option" error instead of the old warning.