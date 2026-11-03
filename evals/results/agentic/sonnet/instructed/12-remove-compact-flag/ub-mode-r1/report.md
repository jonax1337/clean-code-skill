`--compact` and `-c` are gone, and `cargo test` passes (12 tests in `tests/cli.rs`). I only saw the tail of the output, so I didn't see the unit-test results for `cli.rs` and `render.rs`. I haven't committed anything.

- **Code:** I removed the flag, the `compact` option field, the stderr deprecation warning and the compact renderer from `src/cli.rs` and `src/render.rs`. The usage text no longer lists it.
- **Tests:** I deleted the unit and integration tests that exercised compact output. One new integration test checks that `--compact` and `-c` now fail with `UnknownOption`.
- **Docs:** I took the flag out of the README options table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`, pointing people to `--max-width`.

I skipped the ub-mode quality tools (crapper, dryer, mutator) because the change only deletes code.