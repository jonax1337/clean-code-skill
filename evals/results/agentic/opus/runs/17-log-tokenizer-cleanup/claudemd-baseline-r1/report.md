I've split the tokenizer into small, named pieces. My checks show it gives exactly the same tokens and errors as before, and it's about as fast.

## What changed in `src/token.rs`
- The `st: u8` field with values 0/1/2 is now a `State` enum: `Start`, `Value`, `Done`.
- `next()` is now a three-line match that hands off to one function per state: `next_in_start` and `next_in_value`.
- Each kind of token has its own function: `lex_timestamp`, `lex_key_or_word`, `lex_quoted` and `lex_bare`. Each returns `Result<(Token, end), LexError>`.
- Code that used to be copied in many places now exists once:
  - The "set state to 2, jump to end of line, return error" block appeared about 10 times. It's now in `finish()`.
  - `is_separator()` replaces the repeated space-or-tab checks.
  - `expect_separator()` replaces the check after a closing `]` or `"`, which was written twice.
- The public API (`Token`, `Tokens`, `tokenize`) is the same, and nothing allocates.

To add something to the line format, you'll usually add a `lex_*` function and one match arm.

## How I checked that it behaves the same
- I saved a frozen copy of the old tokenizer as `tests/support/reference_token.rs` and added `tests/equivalence.rs`, which compares the two:
  - **Every** line up to 6 characters long built from the characters the tokenizer treats specially (space, tab, `[ ] " \ = n`, a letter, a multi-byte `é`). That's about 1.1M lines.
  - 200k random longer lines.
  - For each line it compares the whole stream: every token, every error with its position, and the `None`s after an error or the end of the line.
- To confirm the test can actually catch a difference, I deliberately shifted one error position by one. Both comparison tests failed.
- `cargo test`: all tests pass (the 8 existing tokenizer tests, 3 stats tests and the 2 new comparison tests). A run of the release binary on the README example gave the expected counts.

## Speed
There's also a timing comparison you run by hand: `cargo test --release --test equivalence -- --ignored --nocapture`. It runs 200k realistic lines through both versions. Over 4 runs (12 rounds), both took about 27–45 ms each round, with neither one consistently faster. So I see no slowdown, but this is a quick timing loop on my machine, not a proper benchmark on your real dumps. If you want certainty, run the nightly import once on a real dump before and after.

One mistake to flag: while undoing the deliberate test break, I ran `git checkout` on `src/token.rs`, which also undid the refactor. That made my first timing run compare the old code with itself. I rewrote the file and ran all the tests and timings above again on the refactored version.

Nothing is committed yet. The changes are `src/token.rs` plus the two new test files.