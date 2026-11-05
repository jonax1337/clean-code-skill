I split the tokenizer in `src/token.rs` into small functions. On my checks it produces the same tokens and errors and runs at the same speed. I haven't committed anything.

**What changed**
- `next()` is now a short dispatcher. It picks the next step from a `State` enum (`BetweenItems`, `ExpectValue`, `Failed`) instead of the old `st: u8` with magic numbers 0, 1 and 2. It also owns the error handling that was repeated about a dozen times (set the position to the end of the line, stop the stream).
- Each token kind has its own scanner: `scan_timestamp`, `scan_key_or_word`, `scan_quoted`, `scan_bare` and `scan_value`, plus small helpers `is_blank`, `skip_blanks` and `expect_separator`. A new piece of the line format means adding one scanner and one match arm.
- The public API is unchanged, and `Tokens` still has the same fields' meaning and `Clone`/`Debug`.

**Checks**
- **Tests:** the existing tests pass (`cargo test`).
- **Same output:** I compared the old and new tokenizers on 2 million random lines built from the format's special characters (`[ ] = " \`, space, tab and letters). Tokens, errors and error positions were identical. This is a differential check, not a proof.
- **Speed:** the first version of the refactor was 10–40% slower. Two changes fixed that: `#[inline(always)]` on the helpers, and having scanners return `(Token, end)` instead of a larger struct. After that, the fastest runs were equal (about 270 ms for 2M lines both ways). The machine was noisy, so I compared the best of 10 runs. I haven't run it on a real dump, so a quick run on one before the nightly import would be worth doing.

The comparison harness is in `/tmp/cmp`, outside the repo. `cargo fmt --check` already complains about `src/error.rs`, and my lines in `token.rs` aren't rustfmt-formatted either. I left formatting alone to keep the diff to the refactor.