I split the tokenizer in `src/token.rs` into one small method per kind of token, and it produces the same tokens and errors as before. Speed looks about the same, but my timings were noisy.

**Structure**
- `next()` now only dispatches on a `State` enum (`Item`, `Value`, `Failed`). This replaces the old `st: u8` with its magic numbers 0, 1 and 2.
- Each token kind has its own method: `timestamp`, `key_or_word`, `quoted`, `bare`, plus `item` and `value` for the two states.
- The repeated "set state, jump to end, return error" blocks became one `fail()` helper. The repeated "next byte must be a blank or the end of the line" check became `check_separator()`.
- To add something to the line format, you now touch one method instead of the whole function.
- The public API (`Token`, `Tokens`, `tokenize`) is unchanged.

**Same output.** I compared the new and old tokenizers on 2 million random lines. The lines were built from characters that trip the lexer: `"`, `\`, `=`, `[`, `]`, tabs and non-ASCII. I compared every token and error, including the error positions and that nothing comes after an error. There were no differences, and the existing tests pass.

**Speed.** My first version was 10–35% slower. That turned out partly to be my benchmark: the old code sat in the test crate and got inlined, while the new code was called across the crate boundary. Comparing both in the same crate, with the helper methods marked `#[inline(always)]`, the difference was within about 5% either way. That is within the run-to-run noise on this machine. I haven't run it on a real multi-GB dump, so do a timing run on the actual nightly import before you merge.

I deleted the temporary comparison and benchmark files, so only `src/token.rs` is modified. Nothing is committed. The existing tests are thin, so you may want to keep a permanent version of the old-versus-new comparison as a regression test. I can add one.