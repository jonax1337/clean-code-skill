I removed `--compact` (and `-c`), and all 26 tests pass. Clippy reports no warnings. Passing either flag now fails with `UnknownOption`.

**What I did:**
1. **Tests first.** In `tests/cli.rs` I replaced the three tests that relied on `--compact` with two new ones: `removed_compact_flag_is_rejected` (checks both flags) and `help_no_longer_mentions_compact`. I also deleted the unit tests for compact mode in `src/cli.rs` and `src/render.rs`. I ran the tests and both new ones failed as expected, because the flags were still accepted and the help text still listed them.
2. **Removed the flag:**
   - `src/cli.rs`: removed the parsing case and its stderr warning, the line in the help text, and the `compact` field on `Options`.
   - `src/render.rs`: removed the compact branch and the two helper functions only it used (`render_compact`, `trim_cells`).
3. **Docs.** I removed the README row and added a "Removed" entry under Unreleased in `CHANGELOG.md`. The entry says to use `--max-width` instead.
4. **Checks.** `cargo test` and `cargo clippy --all-targets` both pass. The only remaining mentions of "compact" are in the new tests.
5. **Commit.** Committed as `767f81f` on `main`. The repo has no remote, so nothing was pushed.

I didn't change the version in `Cargo.toml`, which is still 0.9.0, so you can bump it to 1.0 when you release.