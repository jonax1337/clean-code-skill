I've removed `--compact` (`-c`). `cargo test` passes and `cargo clippy --all-targets` reports no warnings.

**What changed**
- **`src/cli.rs`**: removed the flag from the usage text, the `compact` field from `Options` and its default, the parsing branch with its deprecation warning, and its unit test. Both `--compact` and `-c` now fail with `CliError::UnknownOption`.
- **`src/render.rs`**: removed the compact rendering path and its two unit tests.
- **`tests/cli.rs`**: the three tests for compact output had nothing left to test, so I replaced them with one test that checks both spellings are rejected.
- **`README.md`**: removed the option from the table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased that points users to `--max-width`.

**Breaking API change:** `cli` is a public module, so removing `Options::compact` will break library users who set that field directly. That fits a 1.0 release, but it isn't only a CLI change. The changelog entry only mentions the flag, so you may want to name the field there too.

The version in `Cargo.toml` is still 0.9.0. I haven't changed it or committed anything.