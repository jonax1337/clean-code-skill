I removed `--compact` / `-c`. `cargo test` passes (14 unit tests and 12 integration tests) with no warnings or errors. I didn't run clippy or a formatter.

- **Code:** I removed the flag, its deprecation warning and the `compact` field from `Options` in `src/cli.rs`. I also removed `render_compact` and `trim_cells` from `src/render.rs`, and the `-c` line from the help text.
- **Docs:** I took the flag out of the README table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`.
- **Tests:** I deleted the tests that covered compact output. I added two that check `-c` and `--compact` are now rejected as unknown options: one in `src/cli.rs` and one in `tests/cli.rs`.

Anyone still passing `-c` now gets an unknown-option error instead of the old warning. That is the expected result of removing it.

I haven't committed anything.