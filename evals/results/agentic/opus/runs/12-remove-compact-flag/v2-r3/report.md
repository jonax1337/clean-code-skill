`--compact` and `-c` are removed. `cargo test` passes (13 unit tests, 12 integration tests) and `cargo clippy --all-targets` shows no warnings.

**What changed:**
- **`src/cli.rs`**: removed the flag from the usage text, the `compact` field on `Options`, and the parsing branch that printed the deprecation warning.
- **`src/render.rs`**: removed the compact output path from `render_table`, along with `render_compact` and `trim_cells`. Nothing else used them.
- **`README.md`**: removed the `--compact` row from the options table.
- **`CHANGELOG.md`**: added a "Removed" entry under Unreleased. I left the 0.8.0 "Deprecated" entry as it was.

**Tests:** "Still pass" doesn't mean nothing changed in the tests, so here's what I did. I deleted six tests that checked compact output: one parser test, two render tests and three integration tests. They tested the feature being removed, so they couldn't stay. I added `removed_compact_flag_is_rejected` in `tests/cli.rs`, which checks that both `--compact` and `-c` now fail with `UnknownOption`.

**Before the 1.0 release:**
- Anyone still passing `-c` will now get an "unknown option" error. Before, they got a warning and the output still worked.
- `Options` is public and has lost a field, so any library code that builds it with a literal or reads `.compact` will no longer compile. That's fine for a major version, but it's worth putting in the release notes.
- `Cargo.toml` still says version 0.9.0. I didn't change it.

Nothing is committed.