I took `--compact` / `-c` out and committed it to `main` as `5d484fc`. All tests pass (13 unit, 12 integration) and `cargo clippy --all-targets` shows no warnings.

**One behaviour change to know about:** passing `-c` or `--compact` now fails with the normal unknown-option error. Before, it printed a warning and still ran, so any script that uses it will now break. That's the point of removing it, but the changelog entry says so.

**What changed:**
- **`src/cli.rs`:** removed the flag's parsing and its deprecation warning, the `compact` field on `Options`, its line in the help text, and its unit test.
- **`src/render.rs`:** removed the compact output code and its two unit tests.
- **`tests/cli.rs`:** I replaced the three compact tests with one new test, `removed_compact_flag_is_rejected`, which checks that both `--compact` and `-c` are now rejected. I wrote it first and saw it fail because the flag was still accepted; it passes now.
- **`README.md`:** removed the row from the options table.
- **`CHANGELOG.md`:** added a "Removed" entry under Unreleased that points people to `--max-width`. I left the 0.8.0 deprecation note as it was.

**Not done:**
- I didn't change the version in `Cargo.toml` (still 0.9.0), since deciding when 1.0 ships is up to you.
- I didn't push, because the repo has no remote set up.
- My first scripted edit to `src/render.rs` failed to match, so I finished that file with direct edits. The other files were already updated by then, and the final check found "compact" only in the changelog and the new test.