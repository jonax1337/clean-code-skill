I split the tokenizer in `src/token.rs` into one small method per token kind, with shared helpers for the repeated loops. The output is identical to the original, but I could not prove it is no slower, so please run it on a real dump before merging.

**What changed** (only `src/token.rs`, not committed):
- The old `u8` state is now a `State` enum with three variants: `Start`, `Value` (after `key=`) and `Done` (after an error or the end of the line).
- `Iterator::next` dispatches on the state and turns any error into `Done` in one place. The old code set the state to "done" at each of about ten error returns.
- Each token kind has its own method: `scan_token`, `scan_timestamp`, `scan_key_or_word`, `scan_value`, `scan_quoted`.
- Shared loops are now helpers: `scan_plain` (bare words and values), `find_timestamp_end`, `find_quote_end`, and `check_separator` (the "must be followed by a space, tab or end of line" rule, which was repeated).
- Error positions and the byte-level rules are unchanged.

**Verification**
- `cargo test`: all 11 existing tests pass. `rustfmt --check` is clean. `cargo clippy --all-targets` reports no warnings.
- Differential check: I compiled the original and new `token.rs` side by side in a scratch harness outside the repo (`C:\Users\Jonas\AppData\Local\Temp\tokscratch`). Every line's full output (tokens, errors, and three extra `next()` calls after the end) matched across 4.1M lines: all strings up to 6 pieces from a 10-piece alphabet, plus 3M random longer lines.
- Speed, 600k synthetic log lines (73 MB), interleaved runs:
  - Minimum time: new/old between 0.984 and 1.024 across runs.
  - Median time: new/old between 1.016 and 1.071.
  - So the difference is within run-to-run noise, and I can't say it's strictly no slower. A real dump may show something different.

**Things to know**
- I added `#[inline]` hints to the helpers. Without them the new code was about 1–3% slower in the first runs. Say if you'd rather not have them.
- `Tokens`'s derived `Debug` output changes because its private fields were renamed (`st: u8` is now `state: State`). That is not part of the public API, but anything that snapshots the debug text would notice.