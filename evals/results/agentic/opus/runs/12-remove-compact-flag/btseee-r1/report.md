I've taken `--compact` out, and `cargo test` passes: 25 tests, with no warnings or errors.

**What changed**
- **`src/cli.rs`**: removed the `-c`/`--compact` line from the help text, the `compact` setting, the code that read the flag and printed the warning, and its unit test.
- **`src/render.rs`**: removed the compact output path and its two helper functions, plus their two unit tests.
- **`tests/cli.rs`**: I deleted the three tests that checked compact output. With the flag gone there's nothing for them to check, so this isn't weakening the suite. In their place, one new test checks that `--compact` and `-c` now give the normal unknown-option error.
- **`README.md`**: removed the `--compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased that points people to `--max-width`. I left the old 0.8.0 deprecation note alone because it's history.

**Breaking change:** anyone still passing `-c` or `--compact` will now get an error instead of a warning. That's what the deprecation promised, but it belongs in the 1.0 release notes. I haven't changed the version in `Cargo.toml` (still 0.9.0) and haven't committed anything.