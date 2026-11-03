I've broken the tokenizer in `src/token.rs` into small functions. I checked it against the old version: it produces exactly the same tokens and errors, and it isn't slower. Only that file changed, and the public API is the same. I haven't committed anything.

**How it reads now**
- The `st: u8` magic numbers are now a `State` enum with three states: `Token`, `Value` and `Failed`.
- `next()` is about 10 lines. It picks a handler based on the state, and if the handler returns an error it ends the stream in one place (`fail()`). Before, the "stop after the first error" step was copied out by hand at 13 different return points.
- There is one function per part of the line format: `token`, `value`, `timestamp`, `key_or_word`, `quoted_value` and `bare_value`. They use these shared scanners:
  - `closing_bracket` and `closing_quote` (the quote one also checks escapes)
  - `unquoted_run_end`, which handles the "a `"` here is an error" rule for words, keys and bare values
  - `finish_token_at`, which handles the "a space or tab must follow" rule after timestamps and quoted values
  - `is_separator`
- To add something to the line format, you'll usually write one new function and add one match arm in `token` or `value`.
- The special case for an empty value (`key=` followed by a space or end of line) went away: `bare_value` naturally returns an empty `Bare("")` in that case.
- Everything still works on bytes and borrows from the line. Nothing allocates.

**How I checked it**
- **The 8 existing tests pass**, and clippy has no warnings.
- **Same tokens and errors:** I compiled a copy of the old tokenizer next to the new one and fed both 3 million random lines. The lines were built from the tricky pieces: brackets, quotes, valid and invalid escapes, `=`, tabs, non-ASCII text, and backslashes at the end of a line. For each line I polled the stream 40 times, so it also covered the behaviour after an error or after the end of the line. Every result matched.
- **Speed:** I tokenized 2 million realistic lines (including some with errors) 15 times with each version and took each one's fastest run. In two runs, the old version took 365 / 324 ms and the new one 338 / 315 ms. Timing on this machine is noisy, so I'd call that equal or slightly faster.

**One small difference:** `Tokens` derives `Debug`, so its debug output now shows `state: Token` instead of `st: 0`. The fields are private, so nothing should rely on this.

The comparison harness is in `..\scratch`, outside the repo. It isn't part of the project, so you can delete it, or I can turn the random comparison into a permanent test if you want.