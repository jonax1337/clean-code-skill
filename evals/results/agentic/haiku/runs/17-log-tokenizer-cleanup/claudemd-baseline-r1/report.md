The tokenizer is split into small, named pieces and produces the same tokens and errors as before. It is not slower: in my benchmark it came out about 2% faster. Nothing is committed; the changes are in the working tree.

**What changed**

- `src/token.rs`: the single `next()` function is now a `State` enum (`Start`, `Value`, `Done`) that dispatches to small functions: `timestamp`, `key_or_word`, `value`, `bare`, `quoted`. Shared checks are free functions: `scan_run`, `closing_quote`, `expect_separator`, `skip_blanks`. Errors are produced at the same byte offsets as before. The public API (`Token`, `Tokens`, `Tokens::new`, `tokenize`) is unchanged.
- `tests/tokens.rs`: eight new tests pin the error variants and edge cases that the existing tests didn't cover (nested bracket, missing separator after `]` or `"`, empty key, invalid escape, unterminated quote after a backslash, empty values, `=` inside a bare value). They pass on both the original and the new code.

**Verification**

- `cargo test`: all 3 stats tests and all 16 token tests pass.
- `cargo clippy --all-targets`: no warnings.
- Differential check against a copy of the original file, outside the repo: 4.1 million lines (every string up to length 6 over a character alphabet, plus 3 million random token-level lines). Every token and error matched, with zero mismatches.
- Speed: a synthetic 191 MB corpus of log-shaped lines, release build, best of 12 runs. The new code ran at 0.98× the original's time (262 ms vs 267 ms) in two separate runs.

**Things to know**

- My first version was about 5% slower. Helpers returned `Option<Result<…>>` through extra layers, so I changed them to return `Result<Token, _>` and moved the end-of-line check into `next()`. Adding inline hints didn't help.
- The speed check uses synthetic data, not your real dumps. Run the nightly import (or a sample of a real dump) before merging to confirm.
- `Tokens` derives `Debug`, so its debug output now shows `state: Start` instead of `st: 0`. Nothing in the crate depends on that text, but it is visible if you print a tokenizer.