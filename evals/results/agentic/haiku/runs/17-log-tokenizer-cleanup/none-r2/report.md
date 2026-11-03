I rewrote `src/token.rs` so each token kind has its own scanning method, and the byte-level rules sit in small helpers. Output and errors are unchanged, and it is not slower in my measurements. Nothing is committed.

**What changed**
- The `u8` state code is now a `State` enum (`Token`, `Value`, `Done`). Each state and token kind has a named method: `scan_timestamp`, `scan_key_or_word`, `scan_value`, `scan_quoted`, `scan_bare`.
- Shared rules are helpers: `find_timestamp_end`, `find_quoted_end`, `end_of_token`, `skip_blanks`. Adding a new token form means touching one method and maybe one helper.
- A module doc describes the line format and the state machine.
- The iterator ends the line in one place (`finish`), on end-of-line and on error alike.
- The public API is unchanged.

**Verification**
- `cargo test`: all pass. I added 3 tests to `tests/tokens.rs` for error positions, empty values, and `=` inside bare values, which the old suite didn't cover.
- Differential check: I compiled the original `token.rs` (from git HEAD) next to the new one in a scratch crate outside the repo. I compared the full token and error streams, including the behavior after an error, on about 4.1 million lines: every line up to length 6 over a 10-character alphabet of the relevant bytes, plus 3 million random longer lines. All identical.
- Speed: I benchmarked with a consumer loop that stops at the first error, as `Stats::add_line` does. On 2 million realistic lines the new version measured 0.90× and 0.95× the old time across two runs. The machine is noisy (about ±10% between runs), so this shows "not slower", not a proven speedup. Confirm with your nightly import before relying on it.

**Things to know**
- My first version of the rewrite was about 8% slower, because each scanner returned a nested `Result<Option<Token>>` that `next` re-wrapped. Returning `Result<Token, LexError>` directly fixed it. That's the version now in the file.
- The derived `Debug` output of `Tokens` shows the new fields. This only matters if something logs it.
- `tests/tokens.rs` was already not rustfmt-clean at HEAD, so I didn't reformat it. `token.rs` passes rustfmt, and clippy reports nothing for it.