I removed `--compact` / `-c`, and all tests pass.

**What changed:**
- `src/cli.rs`: removed the flag from the help text, the `compact` field on `Options`, the parsing branch with its warning, and its unit test.
- `src/render.rs`: removed the compact output path, the two functions only it used (`render_compact`, `trim_cells`), and its two unit tests.
- `tests/cli.rs`: removed the three tests that checked compact output and added `removed_compact_flag_is_rejected`, which checks that `--compact` and `-c` now give an `UnknownOption` error.
- `README.md`: removed the option row.
- `CHANGELOG.md`: added a "Removed" entry under Unreleased.

The tests pass because I removed the ones for compact output, not because that behaviour still works. That's expected when a feature is taken out, but it's the part of the diff worth checking.

**Checks I ran:**
- `cargo test`: 13 unit tests and 12 integration tests passed (16 and 14 before; 6 removed, 1 added).
- `cargo clippy --all-targets`: no warnings.
- `git grep -i compact`: the only matches left are the changelog entries and the new test.

**Left alone:** `cargo fmt --check` flags formatting in `src/render.rs` and `tests/cli.rs`, but only on lines I didn't change, so I didn't reformat them here.

Anyone who still passes `-c` will now get an "unknown option" error. That's the planned breaking change for 1.0. I haven't committed anything.