`--compact` (and its `-c` short form) is removed. `cargo test` passes: 13 unit tests and 12 integration tests. Clippy is clean.

**Changes**
- `src/cli.rs`: removed the flag from the help text, the `Options.compact` field, the parser arm with the deprecation warning, and its unit test.
- `src/render.rs`: removed the compact branch, `render_compact`, `trim_cells`, and the two compact render tests.
- `tests/cli.rs`: replaced the three compact integration tests with `removed_compact_flag_is_rejected`, which checks that `--compact` now fails as an unknown option. I added this so the removal is pinned by a test.
- `README.md`: dropped the `--compact` row from the options table.
- `CHANGELOG.md`: added a `Removed` entry under Unreleased. The 0.8.0 deprecation entry stays as history.

**Behavior change:** `-c` and `--compact` now exit with code 2 and `tabulate: unknown option`. Anyone who still passes `-c` will see that error.

**Not done:** `cargo fmt --check` already fails on the untouched `HEAD`, in the `Options { ... }` literals in `src/render.rs` and the `for option in [...]` line in `tests/cli.rs`. I left those alone because they're outside this change. Running `cargo fmt` would fix them, but it would also touch unrelated lines.

I haven't committed anything.