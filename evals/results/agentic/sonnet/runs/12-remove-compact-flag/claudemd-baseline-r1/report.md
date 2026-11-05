I removed `--compact` / `-c`. `cargo test` passes (14 unit tests, 12 integration tests) with no compiler warnings.

- **`src/cli.rs`:** I deleted the flag, the `compact` field on `Options`, the deprecation warning and the help line.
- **`src/render.rs`:** I deleted the compact render path and its two unit tests.
- **Tests:** The three compact integration tests, which checked the flag's output, are replaced by one test. `compact_flag_is_rejected` checks that `--compact` and `-c` now return `UnknownOption`. I did the same in the unit tests.
- **Docs:** I removed the README row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I haven't committed anything.