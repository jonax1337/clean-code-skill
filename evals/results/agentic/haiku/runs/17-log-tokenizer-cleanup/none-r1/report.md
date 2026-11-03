I split the tokenizer in `src/token.rs` into one small function per token kind and kept the same tokens and errors. Speed is the open question. Across five benchmark runs the new version came out at 0.97–1.07× the old time, with a median around 1.04×. This machine's timings swing too much to show parity, so the nightly import is the real test.

**What changed**
- The state is now an enum (`Token`, `Value`, `Done`) instead of a `u8` with magic numbers.
- `next()` only handles the state dispatch and error handling. Each token kind has its own function: `read_timestamp`, `read_word_or_key`, `read_value`, `read_quoted`, `read_bare`, plus `expect_separator` for the "must be followed by a space or tab" rule.
- Adding a line-format rule now means touching one function.
- No allocations or new dependencies. The public API is unchanged.
- The diff is in `src/token.rs` only and nothing is committed.

**Verification**
- `cargo test` passes (8 lib tests and 3 stats tests) and `cargo clippy --all-targets` is clean.
- I built a scratch crate outside the repo that runs the original and new tokenizers side by side. It compared full token streams and exact error values, including positions, over 6M random and structured lines plus every string up to length 5 over a small alphabet. There were no mismatches.

**Performance**
- I benchmarked on a 114 MB synthetic corpus in a release build.
- Using `#[inline]` on the readers, or returning `Option<Token>` through the helpers, measured slower in my runs. I dropped both.
- Replacing the iterator-based scans with plain `while` loops, the style of the original, brought the median from about 1.06× to about 1.04×.

**One thing you may notice:** the `Debug` output of `Tokens` now shows `state` instead of `st`. Nothing depends on that.