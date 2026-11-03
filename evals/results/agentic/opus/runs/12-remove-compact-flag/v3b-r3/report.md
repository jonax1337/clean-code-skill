I've removed `--compact` (and `-c`), and the tests pass.

**What changed:**
- **`src/cli.rs`:** removed the `compact` field from `Options`, the `-c | --compact` arm and its deprecation warning, the line in the help text, and its unit test.
- **`src/render.rs`:** removed the compact rendering path and the two helpers only it used (`render_compact`, `trim_cells`), plus their two unit tests.
- **`tests/cli.rs`:** I took out the three tests for compact output and added `removed_compact_flag_is_rejected`, which checks that both `--compact` and `-c` now fail with an unknown-option error.
- **`README.md`:** removed the row from the options table.
- **`CHANGELOG.md`:** added a "Removed" entry under Unreleased.

**Checks I ran:**
- `cargo test`: 13 unit and 12 integration tests passed, none failed.
- `cargo clippy --all-targets`: no warnings.
- A search for "compact" in `src`, `tests` and the README finds only the new test.

**Before you merge:**
- **Behaviour change:** scripts that still pass `-c` will now get an error and stop, where before they got a warning and output. That's what removing the flag means, but it's worth calling out in the release notes.
- **Version:** `Cargo.toml` is still at `0.9.0`. I left it alone since you'll presumably bump to 1.0 when you release.
- **Formatting:** `cargo fmt --check` already fails on the existing code, so I didn't reformat anything.
- Nothing is committed yet.