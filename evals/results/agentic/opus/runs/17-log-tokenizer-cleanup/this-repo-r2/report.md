The tokenizer is now split into small functions, it gives the same tokens and errors as before, and I measured no slowdown.

**What changed in `src/token.rs`**
- **A named state instead of a number.** The `st: u8` with values 0, 1 and 2 is now an enum with three states: `BeforeToken`, `BeforeValue` and `Failed`.
- **One function per token kind.** `next()` is about 25 lines: it skips separators, picks a function by state, and saves the result. The functions are `scan_token`, `scan_timestamp`, `scan_key_or_word`, `scan_value` and `scan_quoted`. Each returns either the token with where to continue next, or an error.
- **Repeated code removed.** The old code set "fail and stop" by hand in eleven places; now `next()` does it once. Small helpers replace three copies of the separator check after a token and two copies of the "read until a delimiter, but a `"` is an error" loop.
- **Adding to the line format** now usually means adding one `scan_*` function and one match arm.
- Nothing in the public API changed, and there are no new dependencies.

**Behaviour pinned first**
- Before changing anything I added 18 tests to `tests/tokens.rs` that record what the old code does: every error kind with its exact position, empty values (`a= b=`), `=` and brackets inside values, non-ASCII text, a backslash at the end of the line, and that iteration stops after an error. All 26 tests in that file passed on the old code and pass on the new.
- I also ran a throwaway comparison outside the repo: 3,000,000 random lines built from the tricky characters (`[ ] = " \ é`, tabs and so on), each tokenized by the old and new code. All 3,000,000 gave identical results, including the calls after an error or the end of the line. That scratch crate is deleted.

**Speed**
I timed both versions in release mode on 187 MB of realistic lines, 20 rounds each in alternating order, three times:

| Run | Old: fastest / median | New: fastest / median |
|---|---|---|
| 1 | 261 / 335 ms | 241 / 296 ms |
| 2 | 243 / 320 ms | 221 / 332 ms |
| 3 | 202 / 295 ms | 220 / 290 ms |

The differences are within noise. Like the old code, the new code allocates nothing. This was on my machine, not your nightly setup, so I'd time one real dump before relying on it.

**Checks:** `cargo test` passes everything (3 tests in `stats`, 26 in `tokens`) and `cargo clippy --all-targets` gives no warnings.

**Small things to know**
- I renamed the private fields `src` and `st` to `line` and `state`. Code that uses the type isn't affected, but `{:?}` output of a `Tokens` value now looks different. After an error, `pos` is no longer moved to the end of the line. Neither change is visible through the iterator.
- The project isn't run through `rustfmt`. When I ran `cargo fmt` it reformatted other files too, so I undid that and kept the existing style everywhere else.

Nothing is committed.