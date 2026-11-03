I've restructured `src/token.rs`. It produces exactly the same tokens and errors as before and runs at the same speed. Nothing is committed yet.

**What changed**
- The single ~140-line `next()` is now a short dispatcher, plus one small function per token kind: `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_bare` and `lex_quoted`. Each has a doc comment describing the format it accepts.
- The unexplained `st: u8` (0/1/2) is now a private `State` enum: `Token`, `Value`, `Failed`.
- The old code repeated "set state to 2, move to the end, return the error" about a dozen times. Now `next()` does it once: the `lex_*` functions just return their error.
- The repeated logic is in small helpers: `is_separator`, `find` (scan to the first stop byte) and `expect_separator_after`, which runs after a closing `]` or `"`. Adding a new token kind now means writing one new function and adding one line to `lex_token`.
- No public API changes and no `unsafe`; it still borrows every token from the line and allocates nothing.

**How I checked it's the same**
I compiled the old and new tokenizers side by side in a scratch crate outside the repo. It's throwaway and not part of the change.
- **Every short line:** all 11.1M lines up to 7 characters, built from space, tab, `[`, `]`, `"`, `\`, `=`, `a`, `n` and the multi-byte `é`. The tokens and errors matched, including extra `next()` calls after an error or the end of the line.
- **Longer lines:** 3M random lines built from real fragments (timestamps, quoted values with escapes, broken quotes and so on) also matched.
- **Speed:** on 400k realistic lines (about 70 MB, read 10 times per run, 2% malformed), the best of 15 runs was 713 MB/s old vs 710 MB/s new. Over three repeats the gap stayed at 0.5–1%, which is within noise on this machine. I haven't timed the real nightly dumps.

**Tests:** I added two tests to `tests/tokens.rs`. One covers empty and bare values, including `=` inside a value. The other covers every error type that had no test before: `NestedBracket`, `InvalidEscape`, `ExpectedSeparator` after both `]` and `"`, a backslash at the end of a quote, and stray quotes in words and bare values. They pass on both the old and new tokenizer, so they lock in the current behaviour. `cargo test` passes (13 tests) and clippy is clean.

**One visible difference:** printing a `Tokens` iterator with `{:?}` now shows `state: Token` instead of `st: 0`. The internal position also no longer jumps to the end of the line after an error. Neither affects the tokens, the errors or `Stats`.

Should I commit this?