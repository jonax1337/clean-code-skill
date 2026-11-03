I split the tokenizer in `src/token.rs` into small functions. It produces the same tokens and errors as before and isn't slower. I haven't committed anything.

**What changed**
- The 130-line `next()` is now a short dispatcher plus one scanner per token kind: `scan_timestamp`, `scan_key_or_word`, `scan_value`, `scan_quoted` and `scan_bare`. Each scanner returns `Result<(Token, end), LexError>`.
- The magic `st: u8` (0/1/2) became `enum State { Start, Value, Failed }`.
- The `self.st = 2; self.pos = n;` that was repeated for every error now lives in one place in `next()`. Adding a token kind or a rule means adding or editing one small scanner.
- `is_blank`, `skip_blanks` and `expect_separator` replace the repeated `b' ' || b'\t'` checks and the "must be followed by a blank" logic that timestamps and quoted values share.
- The public API (`tokenize`, `Tokens`, `Token`) is unchanged.

**Same tokens and errors**
- Before refactoring I copied the old tokenizer into a test and compared it with the new one on every string up to 7 characters. That was about 5.4 million lines over the format's significant characters (`[ ] " = \ n`, space, tab, `a`).
- Token streams and error variants with their `pos` matched everywhere, and I re-ran it on the final code.
- I then deleted that scaffolding, since the old copy would just be clutter. I added four small tests to `tests/tokens.rs` for edge cases the old tests didn't cover: empty values, missing separators, nested brackets, and bad quotes and escapes. The whole suite passes, with no warnings.

**Speed**
- I timed old against new in release mode on 2.2M synthetic lines, with both compiled the same way. The new code was at parity or slightly ahead on the best of 12 rounds: 857 vs 834 MB/s, then 832 vs 802 on a re-run.
- My first benchmark showed the new code about 20% slower, but that came from the old code being compiled into the benchmark program and the new code being called across a crate boundary. Once both were compiled the same way, the gap disappeared.
- I tried `#[inline(always)]` on the helpers. It made things slower, so I removed it.
- The benchmark used synthetic data. Please run it on a real dump before the nightly job. I'd expect the same result, but a few GB of real lines is the proper check.

I couldn't run the crapper, dryer or mutator tools from the project's guidelines because they aren't installed here. There's no git history for this change yet. I can commit it if you'd like.