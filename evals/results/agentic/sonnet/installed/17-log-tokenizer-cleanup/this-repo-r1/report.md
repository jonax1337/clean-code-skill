I split the one big `next()` in `src/token.rs` into small scanners. It produces the same tokens and errors in every case I tested, but I can't show it's no slower.

**What changed**
- The magic state numbers `0/1/2` are now a private `State` enum (`Field`, `Value`, `Failed`).
- `next()` just dispatches on the state. It is also the only place that handles errors: it sets `Failed` and moves to the end of the line.
- Each piece of the format has its own small method: `timestamp`, `key_or_word`, `next_value`, `quoted` and `bare`. The check that a closing `]` or `"` is followed by a blank or the end of the line was written out twice. It now lives in `finish_delimited`.
- Adding something to the line format now means adding one method and one match arm.
- The public API (`Token`, `Tokens`, `tokenize`) is unchanged. The scanners still work on bytes with no allocation, and a comment explains why slicing stays on character boundaries.

**Verification**
- The existing tests covered very little: two error kinds, no positions for the others. Before touching anything I added `tests/token_edges.rs` with 8 tests. They pin every error with its position, empty values, escapes, multibyte text, and the end of the stream after an error. They passed against the original code first, then against the refactor.
- `cargo test`: all pass (3 + 8 + 8 tests). `cargo clippy --all-targets`: no warnings.
- Speed: I compared the old and new tokenizers on 2M synthetic lines (about 20M tokens), in a scratch project outside the repo, release build, taking the best of 15 runs.
  - Three runs gave −6%, +12% and −1% for the new code. The machine is noisy, so I can't tell this apart from "equal".
  - That input is synthetic, not your dumps. Before it goes into the nightly import, I'd run it once on a real dump file.
- `#[inline]` is on the scanners and `is_blank` to keep the call overhead down. I didn't check the generated assembly.

I didn't touch `escape.rs`, `stats.rs` or the error type. Nothing is committed. `src/token.rs` is modified and `tests/token_edges.rs` is new.