`--compact` and `-c` are gone, and `cargo test` passes (14 unit tests and 12 integration tests, with no compiler warnings).

- **`src/cli.rs`:** I removed the flag parsing, the `compact` field on `Options` and its line in the usage text. Passing `-c` or `--compact` now gives the same "unknown option" error as any other unrecognized flag.
- **`src/render.rs`:** I removed the compact rendering path and its two helper functions.
- **Tests:** I deleted the tests that checked compact output. I added tests in `src/cli.rs` and `tests/cli.rs` asserting that `-c` and `--compact` are rejected as unknown options.
- **Docs:** I dropped the `--compact` row from the README option table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I left the 0.8.0 "Deprecated" changelog entry as it was, since it's release history. Nothing is committed.