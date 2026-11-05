`src/token.rs` is restructured and behaves the same as before. It produces identical tokens and errors, and it is no slower.

**What changed**
- The one `next()` function is split into a method per token kind: timestamp, key-or-word, value after `=`, and quoted value. `next()` only chooses between them.
- The `u8` state number is now an enum (`Between`, `AfterEquals`, `Done`). The repeated `self.st = 2; self.pos = n;` lines are gone. One line in `next()` ends the stream on any error.
- The repeated byte checks became three small helpers: `is_blank`, `scan_unquoted` (which also rejects `"` inside unquoted text), and `expect_separator`.
- The public API is unchanged: `Token`, `Tokens`, `Tokens::new`, `tokenize`, and the `Iterator` impl.
- I added 9 regression tests in `tests/tokens.rs`. They pin the error positions and rules the old tests didn't cover, such as the backslash position for `InvalidEscape`, the separator checks, and nested brackets.

**Verification**
- `cargo test`: 17 pass (8 original, 9 new). Release build has no warnings, and `cargo clippy --all-targets -D warnings` is clean.
- I kept the original file and compared it with the new one in a scratch crate outside the repo. They agreed on all 11,111,111 inputs over a 10-character alphabet up to length 7, and on 3,000,000 random longer inputs. The check also covers what happens after an error.
- To confirm the harness can catch a difference, I moved one error position by a byte in a scratch copy. It reported 16,800 mismatches and failed.
- Timing: on 1M lines (92 MB) of realistic log text, the best of six rounds was 0.123 s new against 0.124 s old, about 1% apart. Run-to-run noise was around ±10%. This measures token iteration only, not the nightly import, so it's worth one run on a real dump before you rely on it.

Nothing is committed. The changes are in the working tree: `src/token.rs` and `tests/tokens.rs`.