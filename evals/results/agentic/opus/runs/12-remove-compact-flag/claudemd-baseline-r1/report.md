I removed `--compact`, and `cargo test` passes: 14 unit tests and 13 integration tests, with no warnings or errors.

**What was removed**
- **`src/cli.rs`:** the `-c`/`--compact` match arm and its deprecation warning, the `compact` field on `Options`, and the line in the help text.
- **`src/render.rs`:** the early return for compact mode and the two functions only it used, `render_compact` and `trim_cells`.
- **`README.md`:** the `--compact` row in the options table.

**Tests**
- I deleted the five tests that checked compact behaviour, since that behaviour no longer exists.
- I added tests checking that `--compact` and `-c` now fail with an `UnknownOption` error, both in the parser and through `run`. Another new test checks that `--help` no longer mentions `--compact`.

**Changelog:** I added a "Removed" entry under Unreleased that points users to `--max-width`. I left the 0.8.0 deprecation entry as it was.

Anyone still passing `-c` or `--compact` will now get an unknown-option error instead of a warning, which is the breaking change promised for 1.0. I didn't change the version in `Cargo.toml` (still 0.9.0), and nothing is committed.