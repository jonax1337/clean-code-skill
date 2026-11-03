I rewrote `src/token.rs` so the tokenizer is split into one small method per token kind, with an explicit state enum. The output and errors are unchanged, and it is no slower than before.

**Verification**
- `cargo test`: all 11 tests pass. Clippy is clean with `-D warnings`, and `token.rs` is rustfmt-clean.
- Differential check against a copy of the original `token.rs`: 3.3 million inputs, zero mismatches. That covers every string up to length 6 over an alphabet containing every delimiter, escape and a multi-byte character, plus 2 million random longer lines and 200k realistic log lines. Each comparison covers the full token stream, error variants and error positions, and checks that the stream stays empty after an error.
- Speed: on a generated 267 MB corpus, the new code ran at 0.87–0.97× the original's time across runs, measured in the same binary. The first draft was 10–18% slower. Adding `#[inline]` to the helpers fixed that, and a comment in the code says to keep them inlined. This is a synthetic corpus, not your dumps, so it's worth timing the real nightly import once.

**What changed**
- `next()` dispatches on a `State` enum (`Token`, `Value`, `Done`) instead of a magic `u8`. Any error moves the stream to `Done`, so the error handling lives in one place.
- Each token kind has its own method: `timestamp`, `key_or_word`, `quoted`, `bare`, plus a shared `expect_separator` check. Adding a field to the line format now means touching one small method.
- The byte checks run in the same order as before, so error positions match.

**Things to know**
- The derived `Debug` output of `Tokens` changed, since the private field is now `state` instead of `st`. Nothing in the public API or the tokens themselves changed.
- The existing tests don't cover `NestedBracket`, `InvalidEscape`, `ExpectedSeparator` or `UnexpectedQuote`. The differential check covers them, but I'd add a few unit tests before the next line-format change.
- The differential harness and benchmark live in `C:\Users\Jonas\AppData\Local\Temp\logscan-diff`, outside the repo. Nothing is committed; the only change is `src/token.rs`.