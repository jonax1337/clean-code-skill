I've split the tokenizer into small functions. It produces exactly the same tokens and errors as before, and in my benchmark it came out a bit faster, not slower. Nothing is committed yet.

**What changed in `src/token.rs`**
- `next()` is now about 25 lines. It skips separators, hands off to one lexing function, and moves the stream to its next state in one place. A key is followed by its value, an error ends the stream, and everything else goes back to looking for the next token.
- The `st: u8` field, which held the magic values 0, 1 and 2, is now a private `Expect` enum: `Token`, `Value` or `Done`.
- Each piece of syntax has its own function: `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_quoted`. Two rules that used to be copied in several places now live in one function each:
  - `scan_unquoted`: unquoted text may not contain `"`.
  - `expect_separator`: a closing `]` or `"` must be followed by a space, a tab or the end of the line.
- The common case for future format changes: a new kind of token is one new `lex_*` function plus one match arm in `lex_token` or `lex_value`.

**How I checked that the output is the same**
- **New tests first:** I added 8 tests to `tests/tokens.rs`, all passing against the old code before I changed anything. They cover the 4 error types that had no tests (`NestedBracket`, `ExpectedSeparator`, `InvalidEscape`, `UnexpectedQuote`) plus edge cases: a backslash at the end of the line, empty values, and values containing `=` or `[`. All 16 tokenizer tests and the 3 stats tests pass, and clippy reports nothing.
- **Old vs new comparison:** a throwaway program, since deleted, ran both versions on 3 million random lines made of the format's special characters (`[ ] " \ =`, space, tab, letters). The tokens, errors and error positions matched every time, including that both return nothing after an error.

**Speed**
I measured both versions in the same release build on realistic log lines, alternating which ran first, over 20 rounds:

| | best | median |
|---|---|---|
| old | 958 MB/s | 778 MB/s |
| new | 1079 MB/s | 948 MB/s |

My first measurement showed the new version about 15% slower. That was because my benchmark always ran the old code first. Once I alternated the order, the gap reversed. Forcing the compiler to inline the new functions didn't help, so the code has no special performance attributes.

The machine was noisy, so treat this as "no slower" rather than a firm 20% gain. The real nightly import over the multi-GB dumps is the true test.

**Two things to know**
- `Tokens` prints differently in debug output (`{:?}`): the `st: 0` field now shows as `expect: Token`. Nothing in the repo uses this, but it is visible from outside the crate.
- `cargo fmt --check` wants to reformat files across the repo, including untouched ones, because the code uses lines wider than rustfmt's default. I followed the existing style and didn't reformat anything.