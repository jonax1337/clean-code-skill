`tabtally add` now takes `--percent NAME=PCT`, and the expense is split by those whole-number percentages. The full suite passes (42 tests, up from 34).

```
$ tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
$ tabtally balances
alice 15.00
bob -9.00
carol -6.00
```

**Choices I made:**
- **`--percent` replaces `--with` rather than adding to it.** The two are mutually exclusive and one of them is required. Mixing them would make it unclear who is in the split.
- **Percentages must total exactly 100.** If they don't, the command fails with `percentages must add up to 100, not 80` and nothing is saved.
- **Each value must be a whole number from 0 to 100.** Anything else, such as `33.5`, `-5` or `150`, is rejected with exit code 2.
- **Cents are split with the existing `allocate()` helper**, so rounding behaves as it already does for equal splits. A 10.00 split three ways still adds up to exactly 10.00.
- **Duplicate names are rejected** for percentage splits too, using the same check the equal split uses (now one shared helper).

**What changed:**
- `tabtally/splitting.py`: new `split_by_percent`; the duplicate check moved into `_reject_duplicates`.
- `tabtally/cli.py`: the `--percent` option, its parser, and the mutually exclusive group.
- `tests/test_cli.py` and `tests/test_splitting.py`: new tests. I wrote them first and saw them fail for the missing feature before implementing.
- `README.md`: one new row in the commands table.

**Not done:** I did not commit or push. The changes are in the working tree for you to review. The ub-mode skill asks for small commits and a push to `main`, but you didn't ask for a commit in this request, so I left that for you to decide. I also did not run the crapper, dryer or mutator tools the skill mentions, because they aren't set up in this repo.