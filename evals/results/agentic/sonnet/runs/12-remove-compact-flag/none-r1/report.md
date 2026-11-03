I removed `--compact` / `-c`, and all tests pass (14 unit, 11 integration) with no compiler warnings. I haven't committed anything.

- **`src/cli.rs`**: I removed the flag, its deprecation warning, the `compact` field on `Options`, and the help line. I replaced the old flag test with one checking that `--compact` and `-c` are now rejected as unknown options.
- **`src/render.rs`**: I removed the compact rendering path and its two unit tests.
- **`tests/cli.rs`**: I removed the three compact integration tests.
- **`README.md`**: I removed the option's table row.
- **`CHANGELOG.md`**: I added a "Removed" entry under Unreleased that points users to `--max-width`.

The 0.8.0 changelog entry still describes the deprecation. That's intentional, since it's history.