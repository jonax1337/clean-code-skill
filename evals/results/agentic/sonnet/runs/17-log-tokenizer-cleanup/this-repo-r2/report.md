I split the tokenizer in `src/token.rs` into small functions, and it produces the same tokens and errors as before. In my benchmarks it is no slower than the old version. I haven't committed anything.

**The new shape**
- `Iterator::next` is now a short dispatcher over a `State` enum (`Field`, `Value`, `Failed`) instead of the old magic `st: u8` with `0`/`1`/`_`.
- `read_field` handles a timestamp, key or word. `read_value` handles the value after a key.
- Small scanners (`scan_timestamp`, `scan_name`, `scan_quoted`, `scan_bare`) each do one job.
- A `#[cold]` `fail` method sets the end-of-stream state in one place, where the old code repeated it at every error site.
- Adding to the line format now means adding one scanner and one match arm.
- The public API (`tokenize`, `Tokens`, `Token`, `LexError`) is unchanged.

**What I ran**
- **Existing tests:** `cargo test` passes with 26 tests (3 in `tests/stats.rs`, 23 in `tests/tokens.rs`).
- **New tests:** the old code had almost no tests, so I added 15 characterization tests to `tests/tokens.rs` first. They cover every error kind and its position, empty values, escapes at the end of a line, multibyte positions, and stopping after an error. They passed against the original code before I changed anything.
- **Old vs new:** I compared the saved original against the new code on 11,411,111 inputs. These were every string up to length 7 over a tricky alphabet (`[ ] " \ = space tab a n é`) plus 300k random longer ones. Tokens, errors and end-of-stream behaviour were identical.
- **Clippy:** clean on the repo code.

**Performance**
- A straightforward split was 30–40% slower, mostly because the helpers weren't being inlined.
- The final version needs `#[inline(always)]` on the five small scanner and helper functions; I left a comment explaining why. Without that attribute, word-heavy lines ran about 15% slower.
- With it, I measured best-of-100 runs per line shape against the old code compiled the same way. They match within noise (about ±5%).
- The realistic mixed line was 2.8–3.0 ms against 3.0–3.4 ms for the old code. Quoted values were about 15–20% faster.
- Word-only lines were sometimes about 3–5% slower. Run-to-run noise on this machine was larger than that.
- **Not tested:** I did not benchmark the real multi-GB dumps. Please compare timings on a real dump before the nightly import depends on this.

**Left alone**
- `cargo fmt --check` reports differences in files I didn't touch (such as `error.rs`), so I didn't reformat.
- I removed the temporary comparison and benchmark files.