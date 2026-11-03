I removed `--compact` (`-c`) completely. `cargo test` passes: 11 integration tests, and the build has no warnings.

- **`src/cli.rs`:** the help line, the `compact` field on `Options`, its default, and the flag parsing with the deprecation warning are gone, along with the unit test for the flag.
- **`src/render.rs`:** I deleted the early return, `render_compact` and `trim_cells`, plus the two compact unit tests. Nothing else used those helpers.
- **`tests/cli.rs`:** I removed the three compact tests. The suite went from 14 integration tests to 11. Those three were the only ones for the flag, so nothing else lost coverage.
- **`README.md`:** the option row is removed.
- **`CHANGELOG.md`:** there is a new "Removed" entry under Unreleased. The 0.8.0 deprecation note stays as history.

`-c` and `--compact` now fail with the existing "unknown option" error. I didn't add a test for that.

I didn't touch the version number in `Cargo.toml`, since you didn't ask for a version bump.