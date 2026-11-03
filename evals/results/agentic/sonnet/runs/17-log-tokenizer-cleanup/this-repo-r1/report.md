I split the one big `next()` in `src/token.rs` into small per-token functions. It produces the same tokens and errors as before, and it isn't slower. I didn't commit anything.

**What changed**
- `next()` is now a short dispatcher. It picks what to read from the current state and handles the "after an error, yield nothing" rule in one place instead of repeating it at every error site.
- Each token kind has its own function: `timestamp`, `key_or_word`, `quoted`, `bare`.
- The "closing delimiter must be followed by a blank" check was duplicated for timestamps and quoted values. It now lives in `finish_delimited`.
- The state is a named enum (`Field`, `Value`, `Nothing`) instead of the magic numbers `0/1/2`. That field is private, so the public API is unchanged.
- Adding something to the line format now means adding or editing one small function.
- The new code still scans the line's raw bytes in a single pass, with no extra allocation.

**How I checked it**
- **Same output:** I kept a copy of the old tokenizer and compared it with the new one on every string up to 7 characters over the alphabet `[ ] " = \ n space tab a`. Tokens, error variants and error positions all matched.
- **Speed:** On 2M synthetic lines in a release build, old and new ran at about 250–290 ms over five rounds, with the new one ahead in four of them. That is roughly on par, and the noise is larger than any difference. I haven't run it on your real dumps, so a quick timing on a slice of one would settle it.
- **Tests:** `cargo test` passes with 15 tests in `tests/tokens.rs`, up from 8, and `cargo clippy --all-targets` is clean.
- **New tests:** I added 7 to `tests/tokens.rs` for cases the old ones didn't cover. They cover separator errors, nested brackets, invalid and trailing escapes, stray quotes (error positions included) and empty values.
- **Cleanup:** I removed the temporary comparison code afterwards.

I left `escape.rs` and `stats.rs` alone.