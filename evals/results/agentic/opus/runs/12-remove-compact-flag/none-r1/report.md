I've removed `--compact`, and `cargo test` passes: 13 unit tests and 12 integration tests. The only place "compact" still appears in the code is a new test that checks the flag is now refused.

**What changed**
- **`src/cli.rs`**: removed the `-c`/`--compact` line from the help text, the `compact` setting, the code that handled the flag and printed the deprecation warning, and its unit test.
- **`src/render.rs`**: removed the compact output mode, the two helper functions only it used, and its two unit tests.
- **`tests/cli.rs`**: replaced the three tests for compact behaviour with `removed_compact_flag_is_rejected`, which checks that both `--compact` and `-c` now fail with the normal unknown-option error.
- **`README.md`**: removed the `--compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased that points users to `--max-width`.

**Behaviour change:** anyone still passing `-c` or `--compact` used to get a warning, but now gets an error. That's expected when removing a deprecated flag, but it does break scripts that still use it.

I left the version in `Cargo.toml` at 0.9.0, so the bump to 1.0 still needs doing when you release. Nothing has been committed.