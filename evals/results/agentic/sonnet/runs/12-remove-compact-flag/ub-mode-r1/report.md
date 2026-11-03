`--compact` and `-c` are gone, and `cargo test` passes with no warnings (14 unit tests and 12 CLI tests). I committed it on `main` as `964d68b` but haven't pushed.

- **Code:** I removed the option, its deprecation warning, the usage line and the compact renderer from `src/cli.rs` and `src/render.rs`.
- **Behavior change:** `-c` and `--compact` are now rejected as unknown options.
- **Tests:** I deleted the compact tests. Two new tests check that both spellings are rejected: one unit test in `src/cli.rs` and one CLI test in `tests/cli.rs`.
- **Docs:** I took the flag out of the README table. The changelog has a new "Removed" entry under Unreleased that points people to `--max-width`.

I didn't run the crapper, dryer or mutator tools from the skill, since the change only deletes code.

Log of actions:
1. Searched for every use of "compact".
2. Read the four affected files.
3. Made the removal edits in one scripted pass.
4. Ran the tests and checked for warnings.
5. Committed.