I've broken the tokenizer in `src/token.rs` into small named pieces. It produces the same tokens and errors as before and isn't slower.

**How it reads now**
- `next()` is a three-way dispatch on a named `State` enum (`Token`, `Value`, `Failed`), replacing the bare `st: u8` with 0/1/2. Error handling now lives in one place: after any error, the stream stops. That replaces the `self.st = 2; self.pos = n;` lines that were repeated 10 times.
- There's one method per token kind: `token()` (skips separators, then decides), `timestamp`, `key_or_word`, `value`, `quoted`, `bare`.
- Each format rule has its own small function: `is_separator`, `skip_separators`, `expect_separator`, `find_timestamp_end`, `find_closing_quote`, and `scan_unquoted`. Keys, words and bare values all share `scan_unquoted`, and the closure says where each one stops.
- To add something to the line format, you'll usually add a `match` arm in `token()` or `value()` plus one scan function.
- The public API (`Token`, `Tokens`, `Tokens::new`, `tokenize`) and its derives are unchanged. `token.rs` grew from 174 to about 190 lines, with less nesting.

**How I checked that behavior didn't change**
- **Tests first:** I added 19 tests to `tests/tokens.rs` and ran them against the original code before refactoring. They cover every error variant and its exact `pos`, plus edge cases such as `a==b` → `Bare("=b")`, `a= b`, `[]`, a backslash at the end of a line, non-ASCII text, and the stream staying empty after an error or the end of the line.
- **Results:** `cargo test` passes all 30 tests (27 in `tokens.rs`, 3 in `stats.rs`), both before and after the refactor. `cargo clippy --all-targets` reports no warnings.
- **Old vs new on random input:** in a scratch crate (since deleted), I ran the old and new tokenizers on 2,000,000 random lines built from the tricky characters (`= " \ [ ]`, tabs, `ä`). The output was identical for every line, errors included.
- **Speed:** a release-mode benchmark over 1,000,000 realistic lines (mostly valid, some rejected), best of 5 runs per round, 3 rounds:

| Round | Old | New |
|---|---|---|
| 1 | 540 MB/s | 634 MB/s |
| 2 | 526 MB/s | 584 MB/s |
| 3 | 506 MB/s | 525 MB/s |

  The machine was noisy, so read this as "not slower" rather than a reliable speedup. The tokenizer still borrows every token and doesn't allocate. I didn't time the real `logscan` binary on an actual multi-GB dump.

**Left alone**
- `cargo fmt --check` fails across the repo, including files I didn't touch (`error.rs`, `tests/stats.rs`). The project uses ~120-column lines without a `rustfmt.toml`, so I followed that style instead of reformatting. Adding a `rustfmt.toml` with `max_width = 120` would make `cargo fmt` match the existing style.
- Some current behavior looks questionable but is now pinned by tests rather than changed: `a==b` gives the value `=b`, and `a=[t]` gives a bare value `[t]`. If either is a bug, fixing it will make the matching test fail on purpose.

Nothing is committed yet.