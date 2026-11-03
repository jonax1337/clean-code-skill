I split the tokenizer in `src/token.rs` into small functions, and it produces the same tokens and errors as before. In a release-build benchmark it ran at the same speed as the old one. All tests pass, and clippy is clean. I haven't committed anything.

**Structure**
- **`next`:** it is now a short dispatch on a named `State` enum (`ExpectingItem`, `ExpectingValue`, `Failed`) instead of the `u8` `0/1/2` codes.
- **One scanner per token kind:** `scan_timestamp`, `scan_key_or_word`, `scan_value`, `scan_quoted` and `scan_bare` each handle one kind. Adding something to the line format now means touching one scanner or adding one.
- **Shared helpers:** `is_blank` and `missing_separator_after` replace the repeated blank checks and the copy-pasted separator check.
- **Errors:** every error goes through one `fail` method that stops further tokens. The old code repeated the same two lines at about a dozen error sites.

**Behaviour**
- I added `tests/equivalence.rs`. It compares the new tokenizer with a frozen copy of the old one (`tests/support/reference.rs`) on every string up to 7 characters over a nasty alphabet. The alphabet includes quotes, backslashes, brackets, `=`, tabs and a multi-byte character. The output has to match exactly, including error variants and positions. It passed on the final version and runs in about 1.5 seconds in a release build.
- Keep that test and the reference copy while you extend the format. Update both deliberately when the format changes on purpose.

**Speed**
- **Comparison:** I benchmarked the old and new code compiled the same way, on 200k lines of mixed quoted, bare and plain-word content. I took the minimum over 100 interleaved rounds.
- **Result:** the ratio was 0.97–1.00 across three runs.
- **Inlining:** the scanners and helpers are marked `#[inline(always)]`. Without it, the split version was about 30% slower, so please don't remove those attributes.
- **Limits of the benchmark:** it used synthetic lines, not your dumps. It's worth timing one real nightly import before relying on it.

I deleted the temporary benchmark.