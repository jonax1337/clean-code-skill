I've taken `--compact` out completely, and the tests pass.

**What changed**
- **`src/cli.rs`**: `-c` / `--compact` are no longer accepted, the `compact` field is gone from `Options`, the deprecation warning is gone, and the help text no longer lists the flag.
- **`src/render.rs`**: removed the separate code path that printed compact rows.
- **Tests**: I deleted the five tests that checked compact output, since that behaviour no longer exists. In their place, one new test in `tests/cli.rs` checks that `--compact` and `-c` are now rejected as unknown options. No other test was changed.
- **Docs**: removed the flag from the README's options table and added a "Removed" entry under "Unreleased" in `CHANGELOG.md`. The 0.8.0 deprecation entry is still there, since it's part of the history.

**Checks**
- `cargo test`: all pass (13 unit tests, 12 integration tests).
- `cargo clippy --all-targets`: no warnings.
- `git grep -i compact`: the only remaining mentions are the changelog and the new test.

**Worth knowing**
- `Options` is public, so removing its `compact` field is a breaking change for anyone using this as a library, not just on the command line. That's expected for 1.0, but it's worth a line in the release notes.
- I left the version in `Cargo.toml` at 0.9.0 because the release wasn't part of this task.

I haven't committed anything.