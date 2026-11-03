I split the tokenizer in `src/token.rs` into one small scanner per token kind. On the benchmark below it's as fast as before, and it gives the same tokens and errors on every line I tried. `Token`, `LexError` and the public API are unchanged.

**What it looks like now**
- **State:** the old magic numbers `0/1/2` are now `State::Field`, `State::Value` and `State::Failed`.
- **Entry point:** `next()` only dispatches on the state, so it fits on one screen.
- **Scanners:** `lex_field` decides between timestamp, key/word and the error cases. `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_quoted` and `lex_bare` each scan one token kind. `escape_len` handles `\"`, `\\`, `\n` and `\t`.
- **Shared pieces:** `is_blank`, `check_separator_after` and `reject` replace the copy-pasted blocks. Each of those blocks used to set the failed state and jump to the end of the line by hand.
- **Adding to the line format:** you now add one scanner and one match arm, instead of editing a 130-line function.

**Same output**
- I compared the new code against the old implementation on every string up to 8 characters over a 10-symbol alphabet (about 111M lines). The alphabet had space, tab, `=`, `"`, `\`, `[`, `]`, `a`, `n` and a multi-byte `é`. Tokens, error variants, error positions and the stop-after-error behaviour all matched.
- I re-ran that comparison on the final code. The existing tests pass, and the release build has no warnings.

**Speed**
- My first version was 35–60% slower in a micro-benchmark, so I didn't stop there.
- That benchmark compared a local copy of the old code against the library across a crate boundary. Once both were local modules, the real gap was 10–25%. I then moved the failed-state handling into the error sites, so `next()` no longer post-processes each result.
- The final check ran `Stats::add_line`, which is what the import uses. It compared a clean checkout of `HEAD` against the working tree on a mix of line shapes, with 200 rounds and the minimum taken. The two were within noise of each other (19.3 vs 18.8 ms, 22.0 vs 22.7 ms, 21.5 vs 19.9 ms).
- I didn't run it on a multi-GB dump. If you want certainty there, time one real dump before and after.

I left the change uncommitted in the working tree and removed all the scratch benchmark and comparison files. I did not add a permanent test for the equivalence check, because it takes about 70 seconds. If you'd like a smaller version in the suite, say so.