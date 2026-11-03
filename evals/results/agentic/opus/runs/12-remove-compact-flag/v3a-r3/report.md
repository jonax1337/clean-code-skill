`--compact` and `-c` are gone, and the tests pass: `cargo test` ran 13 unit tests and 12 integration tests with no failures, and `cargo clippy --all-targets` reported no warnings.

**What I removed:**
- **`src/cli.rs`:** the `-c, --compact` line in the help text, the `Options.compact` field, the code that parsed the flag and printed the deprecation warning, and the `compact_flag_sets_compact` unit test.
- **`src/render.rs`:** the compact branch in `render_table`, the two helpers only it used (`render_compact` and `trim_cells`), and their two unit tests.
- **`README.md`:** the row for the flag in the options table.

**Tests:** I deleted the three tests in `tests/cli.rs` that checked compact output, because that behavior no longer exists. In their place, `removed_compact_flag_is_rejected` checks that both `--compact` and `-c` now return `UnknownOption`. Anyone still passing the flag gets that error.

**Changelog:** I added a "Removed" entry under Unreleased and left the 0.8.0 deprecation note as it was.

**Not done:**
- **Version number:** `Cargo.toml` still says 0.9.0. I didn't bump it to 1.0 because I assumed you'd do that when you release.
- **Formatting:** `cargo fmt --check` already fails on the existing code. Some struct literals in the `render.rs` tests and the option list in `help_lists_every_option` are wider than rustfmt allows. I didn't reformat them, to keep this change to the removal.

I haven't committed anything.