I've split the tokenizer into small functions, one per token kind. It produces the same tokens and errors as before and runs at the same speed. That's checked by a test against a frozen copy of the old code and by a benchmark comparing old and new builds.

**How `src/token.rs` reads now**
- The `st: u8` magic number is now `enum Expect { Token, Value, Done }`.
- `next()` is about 25 lines. It picks the right reader for the current state, then updates the position and state from the result. The rule that an error ends the stream used to be repeated at 14 exits and now lives in one place.
- Each token kind has its own short function: `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_bare` and `lex_quoted`. Each one looks only at the line and returns the token, where it stopped, and what comes next.
- The shared rules have names: `is_blank`, `scan_until` and `expect_separator`. Adding something to the line format usually means adding one `lex_*` function and one match arm.

**How it was verified**
1. **Pinned the old behaviour first (commit `a62446b`).** `tests/oracle` is an unedited copy of the old tokenizer. `tests/equivalence.rs` compares it with the new code on every line of up to 6 characters drawn from space, tab, `[ ] " \ = a n é`, which is about 1.1 million lines, plus some realistic lines. It compares token kinds, the exact byte range each token borrows from the line, and the errors. It also keeps calling `next()` after the stream ends. To make sure the test can fail, I planted a one-character change in the old code's error position and the test failed as expected.
2. **Refactored (commit `64336f8`).** All tests pass, including the 1.1 million-line comparison, and `cargo clippy` reports nothing.
3. **Speed.** `examples/throughput.rs` times a synthetic dump. This machine's timings are noisy, so I alternated old and new builds 12 times each. Best times were 274.9 ms for the new code and 273.5 ms for the old, about 0.5% apart and within the noise. The new build's average was actually a bit lower (322 ms vs 330 ms).
4. **README (commit `78b960c`).** I added a short note on running both checks and on updating the frozen copy when you change the format on purpose.

**Things to know**
- `format!("{:?}", tokens)` on the iterator now prints `expect: Token` instead of `st: 0`. The fields are private, so nothing else is visible from outside.
- The frozen copy is meant to go away. When you next change the line format on purpose, the comparison test will fail; update or delete `tests/oracle` in that same change.
- The workflow you have me use calls for the crapper, dryer and mutator tools, but none of them are installed here, so I didn't run them. The comparison test plus the planted-change check covered the same ground for this change.
- The three commits are on local `main`. The repo has no remote, so nothing was pushed.