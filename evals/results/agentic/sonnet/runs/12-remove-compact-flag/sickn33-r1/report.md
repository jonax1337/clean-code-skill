`--compact` and `-c` are gone. `cargo test` passes (14 unit tests, 11 integration tests) with no warnings. I haven't committed anything.

- **`src/cli.rs`:** I removed the flag, its warning, the `compact` field on `Options`, and its line in the help text. `--compact` and `-c` now fail as unknown options. I added a test, `rejects_the_removed_compact_flag`, that checks this.
- **`src/render.rs`:** I removed the compact rendering path and its two unit tests.
- **`tests/cli.rs`:** I removed the three integration tests that used the flag.
- **`README.md`:** I removed the option's row from the options table.
- **`CHANGELOG.md`:** I added a "Removed" entry under Unreleased, pointing users to `--max-width`.

I didn't touch the version number, since you didn't mention a bump to 1.0.