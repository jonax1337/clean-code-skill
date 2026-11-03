The tokenizer in `src/token.rs` is rewritten as small scanner functions, with the same tokens and errors and no measurable slowdown. Nothing is committed yet.

**What changed**

- `src/token.rs`: the `u8` state and the one long `next()` are replaced by a `State` enum (`Start`, `Value`, `Done`). Each token shape has its own scanner: timestamp, quoted value, key/word, bare value. The "scan until a stop byte, reject a quote on the way" loop, which key/word and bare value both need, now lives in one function, `run_until`.
- `tests/tokens.rs`: two new tests pin every error variant's byte offset and the line-format edge cases (`[t]`, `a=b=c`, `a=`, `ab[c]`). They pass on the original code too, so they describe current behavior.
- Public API is unchanged. The one visible difference is the private `Debug` output of `Tokens`, which now prints `state` instead of `st`.

**Verification**

- `cargo test`: all 13 tests pass. `cargo clippy --all-targets` is clean.
- Differential check (scratch crate outside the repo): every string up to length 6 over an alphabet of 12 characters covering all the grammar's special bytes, plus a multibyte character. That is 3,257,437 inputs. Old and new produce identical token and error output for all of them.
- Speed: on a synthetic 97 MB, 1.5M-line dump, best-of-15 timings give new/old ratios between 0.97 and 1.06 over eight runs, median about 1.01. That is within this machine's noise, so I can say "no measurable slowdown," not "faster." Before the change I measured about 1.09 (slower), which led to the inlining decision below. Please confirm on a real nightly run.

**Choices I made**

- I forced inlining (`#[inline(always)]`) on `run_until`, `scan_key_or_word`, `scan_value` and `expect_separator`. Without it the new code was about 6–9% slower. Those four are the only attributes; the compiler handles the rest.
- The end-of-line check moved into `next()`, so the scanners return a plain `Result`.
- I didn't commit. Your instructions say to commit only when asked, though the ub-mode skill ends with a push. Tell me if you want a commit (I'd use one commit with a message that says what changed and how it was checked).

**Not done**

- The skill's `crapper`, `dryer` and `mutator` tools are not installed here (`cargo mutants`, `cargo crap`, `cargo dryer` all missing). I didn't install them, so there is no CRAP, duplication or mutation score for this change.

**Log**

1. Read `token.rs`, its tests, `error.rs`, `escape.rs`, `stats.rs`, `main.rs`, README; ran baseline `cargo test` (8 pass).
2. Saved the original `token.rs` and `error.rs` to `C:\Users\Jonas\AppData\Local\Temp\cc-scratch-tok\orig` for comparison.
3. Added 2 pinned tests; ran them against the original code (10 pass), so they match current behavior.
4. Rewrote `token.rs` as enum state plus per-token scanners; tests and clippy pass.
5. Built the differential harness and benchmark in `cc-scratch-tok\diff` (outside the repo). First run: 0 mismatches, but about 9% slower.
6. Added `inline(always)` to the four hot helpers: ratio about 0.99.
7. Merged a duplicate match arm in `scan_value`; ran the harness and benchmark again: 0 mismatches, ratio about 1.01 median.
8. Checked line endings: the repo uses CRLF, and the rewritten files match it.