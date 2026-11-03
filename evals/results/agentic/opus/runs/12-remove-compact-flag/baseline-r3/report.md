I removed `--compact` and `-c`. All tests pass: 13 unit tests and 12 integration tests, and the build gives no warnings.

**What changed:**
- `src/cli.rs`: dropped the flag from the help text, the `compact` field on `Options`, and the code that handled the flag and printed the deprecation warning.
- `src/render.rs`: removed the compact output path and the two helper functions only it used.
- `README.md`: removed the `-c`, `--compact` row from the options table.
- `CHANGELOG.md`: added a "Removed" entry under Unreleased that points users to `--max-width`.

**Tests:** six tests checked the compact behaviour, so they couldn't pass once the flag was gone. I deleted them: one in `cli.rs`, two in `render.rs` and three in `tests/cli.rs`. In their place I added one test, `removed_compact_flag_is_rejected`, which checks that `--compact` and `-c` now fail with an `UnknownOption` error. That makes the removal a deliberate breaking change.

I didn't bump the version in `Cargo.toml` or commit anything. Tell me if you want either done as part of the 1.0 release.