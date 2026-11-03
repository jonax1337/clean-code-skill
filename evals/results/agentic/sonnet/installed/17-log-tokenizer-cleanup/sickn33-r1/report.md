I split the big `next()` in `src/token.rs` into small named pieces. Tokens and errors match the old version on 300k random lines. The speed is probably unchanged, but my measurements are too noisy to say for sure. The existing tests pass, and I haven't committed anything.

**What changed**
- The magic `st: u8` (0/1/2) is now a `State` enum: `Field`, `Value` and `Failed`.
- `next()` just dispatches on the state. Each piece of the line format has its own method:
  - `lex_timestamp`
  - `lex_key_or_word`
  - `lex_value`
  - `lex_quoted`
  - `lex_bare`
- `fail()` replaces the "set state, set pos to the end, return the error" block that was repeated 11 times.
- `emit()` and `check_separator_after()` cover the other repeated code.
- `is_separator()` replaces the `b' ' || b'\t'` checks.
- The public API is unchanged: `Token`, `Tokens`, `tokenize` and `Tokens::new`.
- Adding something to the line format should now mean adding or changing one `lex_*` method.

**How I checked it**
- **Same output:** I ran the old and new tokenizers side by side on 300k random lines built from the format's special characters (`[ ] = " \ n t`, space, tab). The `Debug` output of every token and error, including positions, was identical.
- **Speed:** I timed a release build on 200k realistic lines, best of 25 rounds, a few times. The new version landed anywhere from about 10% faster to about 10% slower than the old one between runs, with no consistent direction. An early run without the `#[inline]` hints looked 15–20% slower, so I added the hints to the helpers.
- **Not tested:** your real multi-GB dumps. A run on a real dump before it goes into the nightly import is the safest check.

I removed the temporary comparison test afterwards.