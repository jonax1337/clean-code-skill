I split the tokenizer in `src/token.rs` into small pieces. It still produces the same tokens and errors, and it is not measurably slower. The work is on branch `tokenizer-cleanup` with two commits. I did not merge it into `main`, and I did not push, because the repo has no remote.

**What changed**
- The single 170-line `next()` is now a three-state machine (`Start`, `Value`, `Done`) plus one scanner per token form: timestamp, quoted value, bare value, and key-or-word.
- Each scanner returns the token, the end offset, and the next state. One `emit` method applies that result or ends the stream on error.
- Rules that were repeated in every branch now live in one place: the separator check after each token, the closing-bracket scan, the closing-quote scan with escapes, and the quote rejection inside plain text.
- The module doc describes the grammar and says where to add a new form.
- The largest function is now 18 lines.

**Proof that behaviour is unchanged**
- Before refactoring, I added 6 tests that pin every `LexError` variant with its byte offset, plus empty values, `=` inside bare values, `[` inside words, multibyte text, and blank trimming. They pass on the original code. All 14 token tests pass now.
- A differential harness, kept outside the repo, compares the new tokenizer with a frozen copy of the original. It covers all strings up to length 7 over a 10-byte structural alphabet, plus 3M random lines of length up to 60. Result: 14.1M lines, 0 mismatches.
- I checked the harness itself. A deliberate one-character change (dropping the `\t` escape) was caught by both the harness and a pinning test. The first harness alphabet had a gap: it lacked the letter `t`, so it missed that change. I fixed it before the final run.
- `cargo clippy --all-targets -- -D warnings` is clean.
- Speed: four release-mode runs on 1M lines gave new/old median ratios of 0.93, 1.00, 0.97, and 1.02. The same code measured against itself varied to 0.78 once, so the timing noise is about ±5–25%. I found no measurable slowdown.

**Not done**
- The skill's crapper, dryer, and mutator tools are not installed here. I did not install them. The complexity and duplication checks were manual, and no mutation score was measured.
- I did not push or merge into `main`. Tell me if you want the branch merged locally or pushed once a remote is set up.

**Log**
1. Read `token.rs`, its tests, `error.rs`, `stats.rs`, `lib.rs`, and the README to learn the grammar and what depends on the tokenizer.
2. Found older scratch work in the temp directory. Left it untouched and worked in new directories.
3. Added pinning tests, ran them on the original code, and committed as `6d816cb`.
4. Rewrote `token.rs` as a state machine with per-token scanners, and committed as `c5c6ebe`.
5. Built the differential harness and benchmark outside the repo. Ran them on the original (baseline), then on the refactor.
6. Ran a mutation check: first a sed that didn't apply, then an explicit edit. The restore came from `git checkout`, and I confirmed the tree matched the commit.
7. Fixed the harness alphabet and reran the full check and tests on the restored code. Everything is clean.