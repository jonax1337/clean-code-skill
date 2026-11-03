I removed `--compact` / `-c`, and `cargo test` passes with no warnings: 14 unit tests and 12 integration tests.

- **Code:** I dropped the flag from the usage text and the argument parser, and removed the `compact` field from `Options`. In `src/render.rs` I deleted the compact render path and its helper.
- **Behavior change:** `-c` and `--compact` now fail with the same unknown-option error as any other unrecognized flag.
- **Tests:** I deleted the compact-specific tests. I added two tests that the flag is rejected, one on the parser in `src/cli.rs` and one end-to-end in `tests/cli.rs`.
- **Docs:** I removed the README table row and added a "Removed" entry under Unreleased in `CHANGELOG.md`.

I didn't change the version number. The 1.0 bump is yours to make.