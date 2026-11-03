I split the tokenizer in `src/token.rs` into one small function per token kind. It produces the same tokens and errors as before, and I couldn't measure any slowdown. The change is uncommitted.

**What changed**
- The magic `st: u8` is now a `State` enum with three states: `Item`, `Value` and `Done`.
- `scan_timestamp`, `scan_key_or_word`, `scan_quoted` and `scan_bare` each handle one token kind. Each one returns the token, the next position and the next state, or a `LexError`.
- Small helpers `is_blank` and `expect_separator` replace the repeated space/tab checks.
- `next()` now only stores the result. It also does the "stop after the first error" bookkeeping in one place. Adding something to the line format should mean adding or editing one `scan_*` function and one match arm.
- The public API is unchanged: `Token`, `Tokens`, `tokenize` and `LexError`.

**How I checked it**
- I kept the old implementation temporarily and compared its output with the new one on 3 million random short lines, built from the characters that matter (`[ ] = "`, `\`, space, tab, `n`, `t`). Tokens, error variants and error positions all matched, with 0 mismatches. I then deleted that scaffolding.
- The existing `cargo test` suite passes.
- For speed I ran a release-build benchmark of old against new, tokenizing a typical line 2 million times. The timings were noisy on this machine, and old and new traded places from run to run, so I saw no consistent difference. The scanners are marked `#[inline(always)]` to avoid call overhead. I haven't run it on a real multi-GB dump, so run one nightly import (or a sample of it) before relying on that.

**One difference you can't observe**
- When the line ends, the old code advanced the internal `pos` past trailing blanks. The new code leaves `pos` where it was. This is only visible through `Debug` output of a finished `Tokens`; it has no effect on tokens or errors.

The existing tests are thin: 8 tokenizer tests. If you're going to extend the line format, I can turn the comparison above into a permanent test.