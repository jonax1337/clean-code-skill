I split the tokenizer in `src/token.rs` into small functions. It produces exactly the same tokens and errors as before, and it's just as fast.

**What changed:**
- The state number `st: u8` (0/1/2) is now an enum: `State::Token`, `State::Value` and `State::Done`.
- `next()` is now about 15 lines. It picks what to read next based on the state, and errors are handled in one place: on any error it sets `Done` and moves to the end of the line. Before, the same three lines were copied into 11 error branches.
- Each kind of token has its own function: `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_quoted` and `lex_bare`. Each has a doc comment saying what it reads. The rule "a closing `]` or `"` must be followed by a space, tab or end of line" is now one helper, `expect_separator`, used by both timestamps and quoted values.
- The special case for an empty bare value (`key=` followed by a space or end of line) is gone, because `lex_bare` already returns an empty token there with the same position and state.
- It still works on raw bytes, borrows every token from the line and doesn't allocate. The public API is unchanged.

**How I checked it:**
- **Same output:** I kept a copy of the old tokenizer and ran both on 20 million random lines. The lines were built from the tricky characters: `= " \ [ ]`, spaces, tabs, multi-byte UTF-8, and the escape letters `n` and `t`. For every line I compared the full token stream, including the calls after it ends. All of them matched, and about 9.3 million of those lines hit an error, so the error paths got heavy coverage too.
- **Speed:** I timed both on 29 MB of realistic log lines, five runs each. The new version took between 0.90× and 1.01× the old time, which is the same within noise.
- `cargo test`: all 11 tests pass, and `cargo clippy` gives no warnings.

**One thing that does change:** the derived `Debug` output of the `Tokens` iterator now prints `state: Token` instead of `st: 0`. That only matters if something reads that output, which seems unlikely.

The comparison and benchmark code is in `..\scratch\`, next to the repo and not part of it. You can delete it, or turn it into a proper test or benchmark if you want to keep checking against the old version. I haven't committed anything; the only change in the repo is `src/token.rs`.