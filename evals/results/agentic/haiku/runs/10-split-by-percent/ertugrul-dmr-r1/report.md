`tabtally add` now takes `--percent NAME=PCT`, and the full suite passes (48 tests, up from 34).

```
$ tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
added #1: 30.00 for Pizza
$ tabtally balances
alice 15.00
bob -9.00
carol -6.00
```

**What changed**
- **`cli.py`**: `--with` and `--percent` are in a required mutually exclusive group, so you must use one and can't mix them. Bad `NAME=PCT` input (missing `=`, empty name, non-whole or negative percentage) is reported as `error: ...` with exit code 2 and nothing saved, the same as a bad amount.
- **`splitting.py`**: new `split_by_percent`. It rejects percentages that don't sum to 100 and duplicate names, and reuses the existing `allocate` helper, so cents are never lost. I moved the duplicate check into a shared helper used by both splitters (G5).
- **Tests**: unit tests for the splitter, plus CLI tests for the happy path, a leftover-cent rounding case, the sum-to-100 error, malformed input, and the `--with`/`--percent` conflict.
- **README**: added a row for the new form.

**Choices I made that you may want to change**
- A percentage of `0` is accepted and gives that person a zero share. If you'd rather reject it, it's a one-line check.
- Names are trimmed of surrounding whitespace in `NAME=PCT`.
- The payer doesn't have to be in the split, matching the existing `--with` behaviour.

I haven't committed anything. The changes are in the working tree for you to review.