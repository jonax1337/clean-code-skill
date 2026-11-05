I split the tokenizer in `src/token.rs` into small functions. It produces the same tokens and errors as before, and I measured no slowdown. I haven't committed anything.

**What changed**
- **State:** the magic `st: u8` (0/1/2) is now a `State` enum with `Field`, `Value` and `Done`.
- **Dispatch:** `next()` only dispatches on the state. Each token kind has its own function: `timestamp`, `key_or_word`, `quoted` and `bare`.
- **Shared code:** the repeated "set state to done, jump to the end, return the error" blocks are now one `fail()` helper. The repeated separator check is one `require_separator_after()`, and `is_blank()` replaces the inline space/tab comparisons.
- **Interface:** `Token`, `Tokens`, `tokenize` and `LexError` are unchanged. I didn't touch the loops themselves, so they still scan bytes without copying, as before.

Adding something to the line format should now mean adding one function and one match arm.

**Checks**
- **Existing tests:** all 8 pass, but they're thin.
- **Old vs. new:** in a scratch crate outside the repo, I ran the old and new tokenizers on 3 million random lines built from the format's special characters, plus a multi-byte character. The tokens, error variants and error positions matched on all of them.
- **Speed:** on 2 million realistic lines over 8 rounds, the two stayed within run-to-run noise (about 470–750 ms each, with no consistent winner). That was a synthetic benchmark on this machine, not your multi-GB dumps. Time one real dump before it goes into the nightly job.

I didn't add the random comparison to the repo's tests. It needs the old implementation kept alongside, and the scratch copy is in `..\scratch`. I can write a few more edge-case tests (escapes, separator errors, error positions) if you want a bigger safety net before the next format change.