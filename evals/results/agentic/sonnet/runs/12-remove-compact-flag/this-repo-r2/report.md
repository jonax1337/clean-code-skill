I've removed `--compact` / `-c`, and `cargo test` passes with no compiler warnings (14 unit tests and 12 integration tests).

- **`src/cli.rs`:** I removed the `compact` field and its default, the parsing arm that printed the deprecation warning, and the help line. `-c` and `--compact` now fail with the usual unknown-option error.
- **`src/render.rs`:** I removed the compact branch, `render_compact` and `trim_cells`. Nothing else used them.
- **Tests:** I deleted the tests that covered compact output. I added `rejects_the_removed_compact_flag` in `src/cli.rs` and `compact_flag_is_no_longer_accepted` in `tests/cli.rs`. Both check that the flags are rejected, so a later change can't quietly bring them back.
- **Docs:** I removed the row from the README options table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I didn't touch the version number or `Cargo.toml`, so bumping to 1.0 is still yours to do.