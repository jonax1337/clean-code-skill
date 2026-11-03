The tokenizer is now a set of small functions, it produces exactly the same tokens, errors and error positions, and it isn't slower. Both commits are on `main`. I didn't push because the repo has no remote.

## What changed in `src/token.rs`
- **The state is an enum.** `st: u8` with values 0/1/2 is now `Expect::Token / Value / Nothing`.
- **`next()` is the only place that makes decisions:** it skips separators, picks a lexer, says a key is followed by a value, and stops the stream after an error. Before, the "stop after an error" step was copied 11 times.
- **One function per token kind:** `lex_timestamp`, `lex_key_or_word`, `lex_value`, `lex_quoted`. Each takes the line and a start offset and returns the token and its end, or the error.
- **Shared rules are written once:** `is_separator`, `scan_plain` (a run of unquoted text, where a `"` is an error), `expect_separator` and `find_closing_quote` (which handles escapes).

Adding something to the line format now usually means one new `lex_*` function and one new arm in `lex_token` or `lex_value`.

## How I checked it
- **Tests:** before touching the code I added 14 tests covering every branch, including the 4 error kinds that had no test. All 25 tests pass and clippy is clean.
- **Same output:** I kept a frozen copy of the old tokenizer outside the repo and compared it with the new one. They matched on all 11,111,111 lines of length 0–7 built from space, tab, `[ ] " \ = a n é`, including calling `next()` again after the end. They also matched on 200k generated realistic log lines.
- **Speed:**
  - Tokenizer alone, both versions compiled the same way: the new one is about 20% faster (≈629 vs ≈505 MiB/s).
  - The real `logscan` binary, old vs new, on a 1 GiB / 10M-line dump: 2.879 s vs 2.870 s, with identical output. The whole run takes the same time, so most of it is probably reading stdin; I didn't profile that.
  - Running identical code on both sides varied by about ±6% on this machine, so read these as "not slower" rather than exact numbers.

## Worth knowing
- **One visible difference:** the `Debug` output of a `Tokens` value. The field is now called `expect` instead of `st`, and `pos` no longer jumps to the end of the line after an error. I removed that assignment because nothing reads `pos` once the stream has stopped. Tokens and errors are unaffected.
- **Formatting:** `cargo fmt --check` already failed before this change (e.g. `error.rs`, `tests/stats.rs`), so I followed the existing wide-line style rather than reformatting unrelated files.
- **Tools the skill expects:** crapper, dryer and mutator aren't installed. Instead I relied on the exhaustive comparison, clippy and a manual check for code no test would miss; that check found the `pos` assignment above.
- **The check scripts weren't kept:** I deleted the frozen old tokenizer, the benchmark, the 1 GB dump and the temporary worktree afterwards. Keeping the old copy would mean editing it every time the format changes; the 25 tests in `tests/tokens.rs` are what stays.

## Log
1. Read the code and ran the tests; looked for the skill's tools (not installed).
2. Added and committed the tests that record current behaviour (`c466398`).
3. Built the comparison and benchmark setup outside the repo; measured the noise level.
4. Rewrote `token.rs`; ran the tests, clippy, the full comparison and the benchmarks.
5. Rebuilt the comparison so both versions are compiled the same way, then timed the old and new binaries on 1 GiB.
6. Removed the unused `pos` assignment and the unused derives; re-ran everything.
7. Committed the refactor (`df9187f`), removed the worktree and the scratch directory, and found no remote to push to.