I've taken `--compact` out, and the tests still pass.

**What changed**
- **`src/cli.rs`**: removed the `-c`/`--compact` flag, its deprecation warning, the `compact` field on `Options`, its line in the help text, and its unit test. `-c` and `--compact` now give the usual unknown-option error.
- **`src/render.rs`**: removed the compact rendering code, which nothing else used, and its two unit tests.
- **`tests/cli.rs`**: removed the three tests that checked compact output. In their place, one new test checks that both `--compact` and `-c` are now rejected as unknown options.
- **`README.md`**: removed the row for the flag from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under "Unreleased" that points people to `--max-width`, as the 0.8 deprecation note did.

**Checks**
- `cargo test`: 13 unit tests and 12 integration tests passed, none failed.
- `cargo clippy --all-targets`: no warnings.
- The word "compact" no longer appears in `src/`, the tests or the README, apart from the new test.

**Left alone**
- I didn't change the version in `Cargo.toml` (still 0.9.0). Moving to 1.0 is a release decision for you to make.
- `cargo fmt --check` reports formatting differences in code that was already there. Since the project doesn't seem to run rustfmt, I didn't reformat anything.
- I haven't committed anything.