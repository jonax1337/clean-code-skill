I split the tokenizer in `src/token.rs` into small functions, and I checked it still produces the same tokens and errors at the same speed. It's committed locally as `16673c7` and not pushed.

**New structure**
- `next()` now only looks at the state and picks a scanner.
- There is one scanner per token kind: `timestamp`, `key_or_word`, `quoted` and `bare`. Adding something to the line format means touching one scanner, or adding one.
- `fail()` and `emit()` replace the repeated "set state, set position, return" blocks.
- The state is now a `State` enum (`Start`, `Value`, `Done`) instead of the old `u8` with magic numbers 0, 1 and 2.

**Checks**
- **Same output:** I kept a copy of the old tokenizer and compared it with the new one on every string up to 7 characters. The characters were `a`, space, tab, `=`, `"`, `\`, `n`, `[` and `]`. Tokens, errors and error positions all matched. The existing tests also pass.
- **Not slower:** I timed 200k lines in a release build. The old and new versions ran in the same 28–32 ms range, with neither consistently ahead.

**Things to know**
- My first attempt was about 25% slower. The cause was the way I wrote the bounds checks, so I went back to the original loop shapes, and the helpers are marked `#[inline(always)]`.
- I didn't commit the comparison test or the old copy, because it would leave a duplicate tokenizer in the repo. If you want a permanent safety net before the next format change, I can add a smaller test that checks a list of tricky lines against fixed expected output.
- My benchmark covered one synthetic line shape, not your real dumps. Run the nightly import once on a real dump to confirm.