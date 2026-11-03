I've removed `--compact` and `-c`, and `cargo test` passes: 14 unit tests and 12 integration tests.

**What changed:**
- **`src/cli.rs`**: removed the flag from the help text, the `compact` field on `Options`, and the code that printed the deprecation warning. Both `--compact` and `-c` now fail with an unknown-option error, like any other unrecognised flag.
- **`src/render.rs`**: removed the compact output path and the helper functions only it used.
- **Tests**: deleted the five tests that checked compact output. I replaced them with a unit test and an integration test that check the removed flag now gives an unknown-option error, so it can't come back by accident.
- **Docs**: took the flag out of the README's options table and added a "Removed" entry under "Unreleased" in `CHANGELOG.md`, pointing people to `--max-width` instead.

Two things to know:
- **Breaking change:** scripts that still pass `-c` or `--compact` will now fail instead of printing a warning. That's what the 0.8 deprecation notice said would happen.
- **Version not changed:** I left the version in `Cargo.toml` at 0.9.0 because you'll probably change it when you cut the 1.0 release.

Nothing is committed yet.