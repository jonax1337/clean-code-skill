I've rewritten `src/token.rs` so it's easier to read. It produces exactly the same tokens and errors as before, and it isn't slower. Only that file changed, and nothing is committed yet.

**What changed**
- **Named states:** the `st: u8` with states 0, 1 and 2 is now a private `Expect` enum with `Token`, `Value` and `Nothing`.
- **Short `next()`:** it now just picks a reader based on the current state. If the reader returns an error, it stops the stream. Before, that stop code was copied out at all nine error returns.
- **One small method per token kind:** `read_token`, `read_timestamp`, `read_key_or_word`, `read_value`, `read_quoted` and `read_bare`.
- **Byte-scanning helpers:** `skip_separators`, `find_timestamp_close`, `find_quote_close`, `find_unquoted_end` and `require_separator_at`. Each one finds a position or returns the matching `LexError`, and is used with `?`. Two things that were written out several times now live in one place each: the "space or tab" check (`is_separator`) and the "must be followed by a separator" check.
- **Adding to the line format:** this usually means a new arm in `read_token` or `read_value` plus one helper, rather than more nesting in the big function.

The public API (`Token`, `Tokens`, `tokenize`, `Tokens::new`) is unchanged. It still works directly on bytes, borrows everything from the line and doesn't allocate. The only visible difference is the `{:?}` output of a `Tokens` value itself, which now shows `expect: Token` instead of `st: 0`. The tokens it yields print the same as before.

**How I checked it**
- **Same output:** I kept a copy of the old tokenizer and ran both on 5.4 million lines. These were every line up to 7 characters built from `[ ] " \ = space a n`, plus 3 million random lines that included tabs, multi-byte UTF-8, and valid and invalid escapes. Every token, every error and its byte position, and the `None` after an error matched.
- **Speed:** on a 200 MB generated dump, the old version took 398–493 ms per run and the new one 341–415 ms, over 5 runs each. The numbers are noisy, but it's at least as fast as before. This was a synthetic dump, so it's worth confirming on a real nightly file.
- **Repo checks:** `cargo test` passes (11 tests) and `cargo clippy --all-targets` reports no warnings.

The comparison and benchmark code is in `..\scratch`, next to the repo and not part of it. You can rerun it with `cargo run --release` or delete it. If you'd like the old-versus-new comparison kept as a permanent regression test in `tests/`, I can add it.