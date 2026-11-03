I removed `--compact` (`-c`). All tests pass (13 unit, 12 integration) and clippy reports nothing.

**What changed**
- **`src/cli.rs`**: removed the flag from the help text, the `compact` field on `Options`, the deprecation warning, and its parser branch. `-c` and `--compact` now fail with `UnknownOption`, the same as any other unknown flag.
- **`src/render.rs`**: removed the compact branch and the two functions only it used, `render_compact` and `trim_cells`.
- **Docs**: removed the README table row and added a "Removed" entry under "Unreleased" in the CHANGELOG.

**About the tests:** five tests checked the compact output itself, so they couldn't stay once the feature was gone. I deleted them and added one integration test, `removed_compact_flag_is_rejected`, which checks that both spellings are now rejected. No other test was changed.

**Not done:**
- `Cargo.toml` still says version 0.9.0. I left the bump to 1.0 to you.
- `cargo fmt --check` was already failing before this change, mostly on one-line struct literals in tests. I left those lines alone so the diff stays limited to the removal.
- Nothing is committed yet.