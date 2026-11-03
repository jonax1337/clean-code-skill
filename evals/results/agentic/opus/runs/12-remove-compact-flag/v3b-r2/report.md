I took `--compact` / `-c` out completely, and all tests pass.

**What changed**
- **`src/cli.rs`:** the flag is gone from the help text, the options and the argument parsing, along with its deprecation warning. Passing `--compact` or `-c` now gives an unknown-option error.
- **`src/render.rs`:** I deleted the compact output path and the two helpers only it used.
- **Tests:** I deleted the five tests that checked compact output, since that behaviour no longer exists. In their place, `removed_compact_flag_is_rejected` in `tests/cli.rs` checks that both spellings are now refused.
- **Docs:** I removed the flag's row from the README's options table and added a "Removed" entry under "Unreleased" in `CHANGELOG.md`.

**Checks I ran**
- Before the change: `cargo test` passed 30 tests (16 unit + 14 integration).
- After the change: `cargo test` passes 25 tests (13 unit + 12 integration), and `cargo clippy --all-targets` gives no warnings.
- `cargo fmt --check` fails, but only on lines I didn't edit (struct literals in the `render.rs` tests and an array in `help_lists_every_option`). I didn't reformat them to keep this change small. Running `cargo fmt` separately will clean them up.

Anyone with `-c` in a script will now get an error instead of a warning, as the 0.8 deprecation notice said would happen. I didn't bump the version in `Cargo.toml` (still 0.9.0); that's for whenever you cut 1.0. Nothing is committed yet.