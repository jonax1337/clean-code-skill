`--compact` (`-c`) is gone, and `cargo test` passes: 13 unit tests and 12 integration tests, no warnings.

Changes:
- **src/cli.rs**: removed the `compact` field and its default, the `-c`/`--compact` parse arm with its deprecation warning, the usage line, and the flag's unit test.
- **src/render.rs**: removed the compact branch in `render_table`, plus `render_compact`, `trim_cells`, and their two tests. `join_lines` stays, since the normal renderer uses it.
- **tests/cli.rs**: replaced the three compact tests with `removed_compact_flag_is_rejected`, which asserts both `--compact` and `-c` now return `UnknownOption`. I ran it before the code change and it failed as expected (the flag was still accepted).
- **README.md**: removed the `-c` row from the options table.
- **CHANGELOG.md**: added a `Removed` entry under Unreleased.

Choices to check:
- Anyone still passing `-c` will get an "unknown option" error, not a silent ignore. That's the usual meaning of removal, but it is a breaking change for scripts that still use it.
- I didn't bump the version or commit anything. Tell me if you want a commit, and with what message.