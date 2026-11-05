I split the tokenizer in `src/token.rs` into small functions. It produces the same tokens and errors as before, and I couldn't measure a slowdown. Only that file changed, and I haven't committed anything.

**What changed**
- `next()` is now a short dispatcher on a three-case `State` enum (`Field`, `Value`, `Failed`). That replaces the old `st: u8` with its magic values 0, 1 and 2.
- Each construct has its own scanner: `scan_timestamp`, `scan_key_or_word`, `scan_quoted`, `scan_bare`, plus `scan_field` and `scan_value` to route between them.
- Shared helpers (`is_blank`, `skip_blanks`, `expect_separator`) replace the repeated space/tab checks and the separator check.
- The scanners return `Result<(Token, next_pos), LexError>`. The "set state to failed and jump to the end of the line" step now lives in one place instead of about 15.
- To support a new construct, add a `scan_*` function and one match arm.
- `Token`, `Tokens`, `tokenize` and the public API are unchanged. The scanning is still byte-level over the borrowed `&str`, with no allocation.

**Checks**
- The 8 existing tests pass.
- I compared the old and new code on 3 million random lines built from the format's special characters (`[ ] = " \ space tab`, escapes and so on). The full token and error sequences, including error positions, were identical every time.
- On a representative line over 2 million iterations, the old and new versions ran about the same: roughly 300–440 ms each, with the order flipping between rounds. That was a quick check on a noisy Windows machine, not a rigorous benchmark.
- I didn't run it on real multi-GB dumps. Run your nightly import once before and once after, and compare the two timings.