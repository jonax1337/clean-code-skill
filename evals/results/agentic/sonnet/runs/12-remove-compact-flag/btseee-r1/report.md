`--compact` and `-c` are gone, and `cargo test` passes (12 integration tests, 0 failures).

- **Code:** I removed the flag, the `compact` field on `Options`, its deprecation warning and its usage line from `src/cli.rs`. I also removed `render_compact` and its helper from `src/render.rs`.
- **Tests:** I deleted the tests that only covered compact mode. I added `removed_compact_flag_is_rejected` in `tests/cli.rs`, which checks that `--compact` now returns `UnknownOption`.
- **Docs:** I removed the option from the README table. I added a "Removed" entry under Unreleased in `CHANGELOG.md`.

The changelog says "Use `--max-width` to keep output narrow", copied from the 0.8 deprecation notice. That isn't a real replacement, because `--max-width` truncates cells and doesn't remove padding. Say if you'd like that sentence reworded or dropped.

I haven't committed anything.