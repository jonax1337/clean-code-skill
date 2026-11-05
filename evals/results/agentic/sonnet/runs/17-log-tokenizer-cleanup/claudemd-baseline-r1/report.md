I split the tokenizer in `src/token.rs` into small pieces. Tokens and errors are unchanged, and I measured no slowdown. The tests pass after my last edit (`cargo test --release`, no warnings). I haven't committed anything.

**What changed**
- The `st: u8` state is now a `State` enum with `Item`, `Value` and `Failed`.
- `next()` just dispatches on that state. The separate `next_item` and `next_value` methods handle token starts and values.
- The scanning rules now live in small functions, each with a doc comment: `scan_timestamp`, `scan_quoted`, `scan_run` and `check_separator`. A new line-format feature should only need a new scanner and a new match arm.
- The `fail` and `emit` helpers replace the repeated "set state, set pos, return" blocks.
- The public API is unchanged.

**How I checked it**
- I added `tests/equivalence.rs`. It holds a frozen copy of the old function and compares it with the new one on every string up to 6 characters over a 10-character alphabet. The alphabet covers blanks, brackets, quotes, `=`, backslash, `n`, `a` and a multibyte character. That is about 1.1 million lines, and the tokens and error positions all match. It also runs a handful of realistic and malformed lines. The suite takes about 2 seconds. You can delete the test once you trust the refactor.
- The existing tests in `tests/tokens.rs` and `tests/stats.rs` also pass.

**Speed**
- I timed old against new on a throwaway benchmark, 3M iterations of one realistic line, in release mode. My first version was consistently about 4–6% slower, so I restructured. The final version is on par, with run-to-run noise of about ±10%.
- I have no multi-GB dump to test on. Before you rely on it for the nightly import, run it once against a real dump.
- I removed the benchmark file.