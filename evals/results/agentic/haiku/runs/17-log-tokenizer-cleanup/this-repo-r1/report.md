I refactored `src/token.rs` so each line format rule has its own small function, and the output is unchanged: same tokens, same errors, same positions. It's not committed.

**What changed**
- The `st: u8` field is now a `State` enum (`Start`, `Value`, `Done`).
- Each case has its own function: timestamp, quoted value, bare run, key/word, and value after `=`. Helpers handle the separator check and the end-of-value scan.
- `next()` does the state and position bookkeeping in one place. Every error goes through a single branch that moves to `Done`.
- Adding a new line-format rule now means touching one scanner function, not one large match.
- The public API is unchanged. The one visible difference is the derived `Debug` output of `Tokens`, which now shows `state` instead of `st`.

**Verification**
- `cargo test`: all 3 stats tests and all 15 token tests pass. Clippy and rustfmt are clean.
- I added 7 tests to `tests/tokens.rs` for edge cases the old tests didn't cover: empty values, `a==b`, quotes inside words, invalid escapes, and separator errors after `]` and `"`. They also pass on the original code, so they pin existing behavior.
- Differential test against a copy of the original tokenizer, kept in a scratch crate outside the repo: all 5,380,840 lines up to length 7 over a tricky byte alphabet, plus 300,000 random lines with multibyte text. Identical tokens and errors in every case.
- I checked the differential test can fail: a deliberate change to the escape set was caught once the alphabet included `r`.

**Performance**
- Benchmarked `Stats::add_line` (the nightly import's path) on 2M synthetic lines, old and new builds alternating over 10 runs. Minimum 207.0 ms new vs 223.7 ms old; mean 223.6 vs 239.2 ms. The machine is noisy, so the honest reading is "not slower", and possibly a few percent faster.
- An earlier harness that called `tokenize` across a crate boundary showed a gap of about 2–3%. That's an artifact of cross-crate inlining, not how the import calls the code, so I didn't optimize for it.
- I didn't time a real dump. Before merging, run the nightly import on a sample of real data to confirm.

**Notes**
- I didn't reformat the existing test file. My first rustfmt pass rewrapped the existing tests, so I restored that file from git and added only my new tests.
- The scratch harness (differential test and benchmarks) lives in `%TEMP%\logscan-scratch` and is not in the repo.