I split the tokenizer in `src/token.rs` into small functions. It produces the same tokens and errors as before, but I couldn't make it as fast as the old version. In my benchmarks it is about 5–10% slower on realistic lines, and up to roughly 20–30% slower on lines made only of short `key=value` pairs. Nothing is committed, and `src/token.rs` is the only file changed.

**Behaviour.** I compared old and new on every string up to 8 characters over `[ ] " = \ space tab a n`, which is about 54 million inputs. Tokens, error variants and error positions all matched, and the iterator still yields nothing after the first error. I deleted the comparison test and the benchmark afterwards, since they depended on a copy of the old code. The existing tests pass.

**Structure.**
- **Dispatch:** `next()` picks the handler from a `State` enum (`BetweenTokens`, `AfterEquals`, `Failed`) instead of the magic `0/1/2`.
- **Lexers:** one per token kind: `lex_timestamp`, `lex_key_or_word`, `lex_bare`, `lex_quoted`. Each returns the token, the position after it and the next state.
- **Scanners:** small helpers for the repeated pieces: `find_timestamp_end`, `find_closing_quote`, `require_separator_after`, `is_valid_escape`.
- **Error handling:** the `st = 2; pos = n; return Err(..)` block, which appeared about 15 times, now lives in one place (`Tokens::fail`).
- **Adding something to the line format:** this should now mean adding one lexer and one match arm.

**Performance.** I benchmarked old and new compiled the same way, over a few hundred thousand lines. My first comparison was misleading because the old code could be inlined into the benchmark loop and the new one couldn't. After fixing that, the slowdown persisted. Several variants made no difference: forced inlining, returning the state from each lexer, and different loop shapes. Using slice iteration in the scanning loops helped the most. I'm not sure where the rest comes from. My guess is the extra layer of results between the lexers and `next()`.

Decision for you: keeping the speed exactly means going back to something close to the original single-function loop. The alternative is to accept the small slowdown for the readability gain. Before you merge this, run it on one of your real dumps, because my numbers come from synthetic lines.