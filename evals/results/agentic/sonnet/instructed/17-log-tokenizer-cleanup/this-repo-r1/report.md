I split the tokenizer in `src/token.rs` into small byte-scanning functions. It produces the same tokens and errors as before and runs at the same speed. I haven't committed anything.

**What changed**
- `next()` is now a short dispatch over a three-variant `State` enum (`Field`, `Value`, `Failed`). That replaces the `st: u8` with its magic 0, 1 and 2.
- Each piece of the line format has its own function: `timestamp`, `key_or_word`, `bare`, `quoted`, `skip_blanks`.
- The "closing delimiter must be followed by a blank or the end" check was written twice, once for timestamps and once for quoted values. It is now one function, `finish_delimited`.
- The "scan to the end, error on a stray `"`" loop was written twice, once for keys and words and once for bare values. It is now one function, `unquoted_end`. It takes a closure for where to stop, so the compiler specializes each use.
- Errors are no longer set by hand at each failure site. A scanner returns `Err`, and `next()` parks the tokenizer in one place.
- To add something to the line format, you now add a scanner function and one arm in `next_field`, or one branch in `next_value` for a value type.

**How I checked it**
- The existing tests only covered a few of the error paths. Before refactoring, I compared the old and new tokenizers on every string up to 7 characters over `a`, space, tab, `[`, `]`, `"`, `=`, `\`, `n` and `x`. That is about 11 million lines, and every token and error matched exactly, including positions and the stop after the first error.
- Speed: 2M tokenizations of a typical line took about 280 ms on both, in a release build. Run-to-run noise was around 10 ms, so I see no slowdown. I did not run it on a real dump.
- I added 8 permanent tests to `tests/tokens.rs` for edge cases the old tests missed. They cover:
  - `key=` followed by a space or the end of the line
  - a missing separator after `]` or after a closing quote
  - a nested `[`
  - an invalid escape
  - a trailing backslash
  - stray quotes
  - `=` inside a bare value
- `cargo test`: all pass (16 tokenizer tests, 3 stats tests). I deleted the temporary comparison harness.

**Left alone**
- Strings containing non-ASCII bytes weren't in the comparison. The delimiters are all ASCII, so the slicing is unchanged.
- Some behavior looks odd but is preserved, and the new tests pin it. One example: a bare value like `a=b=c` keeps the second `=`.