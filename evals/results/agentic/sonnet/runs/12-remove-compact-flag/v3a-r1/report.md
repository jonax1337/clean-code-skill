`--compact` and `-c` are gone, and `cargo test` passes (14 unit tests and 11 integration tests, no warnings). I didn't run clippy or a formatter.

- **Code:** I removed the `compact` field from `Options`, the argument parsing and its deprecation warning, the help line, and the `render_compact` and `trim_cells` helpers in `src/render.rs`.
- **Tests:** I deleted the tests that covered compact output. I added `rejects_the_removed_compact_flag` in `src/cli.rs`, which checks that `--compact` and `-c` now return `UnknownOption`.
- **Docs:** I removed the README table row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

The Cargo version is still 0.9.0, so you'll need to bump it to 1.0 yourself. I made no commit.