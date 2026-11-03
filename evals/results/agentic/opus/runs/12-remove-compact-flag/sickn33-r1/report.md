I've removed `--compact`, and all 26 tests pass (14 unit, 12 integration) with no compiler warnings.

You said the tests should still pass, but I couldn't keep all of them as they were. Five tests (two unit tests in `src/render.rs` and three integration tests in `tests/cli.rs`) existed only to check that `--compact` works, so I deleted them along with the feature. In their place I added two tests that check `--compact` and `-c` are now rejected with an "unknown option" error.

**What changed:**
- **`src/cli.rs`**: removed the `compact` setting, the code that read `-c`/`--compact` (including its deprecation warning), and its line in the help text.
- **`src/render.rs`**: removed the code that printed compact output.
- **`README.md`**: removed the `--compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under "Unreleased" that points people to `--max-width`.

This is a breaking change: anyone still passing `-c` or `--compact` will now get an error instead of a warning. I left the version in `Cargo.toml` at 0.9.0, so it still needs to become 1.0.0 when you release. Nothing is committed yet.