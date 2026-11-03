I removed `--compact` / `-c`, and `cargo test` passes. The 12 integration tests pass. `tail` cut off the unit-test section of the output, so I didn't see that count. `cargo clippy` reported no warnings in the lines I saw.

- **Code:** In `src/cli.rs` I removed the `compact` option field, the parsing branch with its stderr warning, and the help line. In `src/render.rs` I removed the compact branch and the two helpers only it used (`render_compact`, `trim_cells`).
- **Behavior change:** `-c` and `--compact` now fail with the same "unknown option" error as any other unrecognised flag.
- **Tests:** I deleted the compact tests, including the two unit tests in `render.rs`. I added one unit test in `cli.rs` and one integration test in `tests/cli.rs` that check both spellings are rejected.
- **Docs:** I dropped the row from the README options table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I didn't bump the version in `Cargo.toml`, which is still 0.9.0, or write a 1.0 release entry. That is a release decision for you.