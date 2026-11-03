I split the tokenizer in `src/token.rs` into small functions, and it produces the same tokens and errors as before. It also isn't slower.

**What it looks like now**
- The magic `st: u8` (0/1/2) is now a `State` enum with `Item`, `Value` and `Failed`.
- There is one small function per token kind: `timestamp`, `key_or_word`, `quoted` and `bare`. `item` and `value` pick between them, and `next` just dispatches on the state.
- Two helpers replace the code that was repeated all over the old function. `fail(err)` records an error and stops the iterator. `check_separator(end)` handles the "must be followed by a blank" rule.
- Adding something to the line format now means adding one function and one `match` arm, not editing a 130-line function.
- The public API is unchanged: `Token`, `Tokens`, `Tokens::new` and `tokenize`.

**How I checked it**
- The existing 8 tests pass.
- I ran the old and new tokenizers side by side on 2 million random lines built from the characters that matter (`[ ] " \ = space tab` and non-ASCII). Every token, error and error position matched.
- I timed both on 200k realistic lines in a release build. Over 15 rounds the best time was about 31 ms for the new code against about 40 ms for the old, so it is no slower and probably slightly faster. I only ran this on that synthetic input, not on your multi-GB dumps. The numbers are noisy, so don't read the gap as a guaranteed speedup.

The fuzz and benchmark harness is a scratch crate in `/tmp/diff`, not in the repo. I haven't committed anything.

I'd suggest adding a few edge-case tests to `tests/tokens.rs`. They would cover the invalid escape, the nested `[`, the missing separator after `]` or a closing quote, and `key=` at the end of a line. Today only some of the error paths are tested, and the fuzz run was the only check on the rest.