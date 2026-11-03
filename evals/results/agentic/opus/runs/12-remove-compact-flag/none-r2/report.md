I've removed `--compact`, and `cargo test` passes: 14 unit tests and 12 integration tests, with no compiler warnings.

**Code**
- `src/cli.rs`: removed `-c`/`--compact` from the help text, the `compact` field on `Options`, and the code that read the flag and printed the deprecation warning.
- `src/render.rs`: removed the compact output path and the two helper functions it used (`render_compact` and `trim_cells`).

**Tests:** I couldn't leave the existing compact tests in place, because they checked the flag's output and would fail now that it's gone. Instead of just deleting them, I replaced them with tests that check `--compact` and `-c` are rejected as unknown options, in both `src/cli.rs` and `tests/cli.rs`.

**Docs:** I removed the `--compact` row from the README options table and added a "Removed" entry under "Unreleased" in `CHANGELOG.md`. The 0.8.0 deprecation note is still there.

This is a breaking change: anyone still passing `-c` or `--compact` will now get an unknown-option error instead of a warning. That's what the deprecation promised, so it fits a 1.0 release. I haven't committed anything.