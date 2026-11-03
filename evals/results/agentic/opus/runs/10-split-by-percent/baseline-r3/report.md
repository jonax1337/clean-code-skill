I've added `--percent NAME=PCT` to `tabtally add`, and all 50 tests pass (34 old, 16 new). Nothing is committed yet.

```console
$ python -m tabtally add --paid-by alice --amount 100 --description Groceries --percent alice=50 --percent bob=30 --percent carol=20
```

**How it behaves:**
- You use either `--with` or `--percent` on an `add`, not both. Giving both, or neither, is rejected.
- **Rounding:** the split goes through the same rounding code as equal splits, so the shares always add up to the full amount. For example, 0.01 split 50/50 becomes 1 cent and 0 cents.
- **Rejected input:** each of these gives an `error:` message, exits with code 2 and saves nothing:
  - percentages that don't add up to 100
  - a value that isn't a whole number, like `12.5` or `abc`
  - a value missing its `=`, name or number
  - the same person listed twice

**One choice to check:** I made 0% invalid, so every percentage has to be at least 1. Allowing someone at 0% would be a small change if you want it.

**Changes:**
- `tabtally/splitting.py`: new `parse_percent` and `split_by_percent`.
- `tabtally/cli.py`: the new option, plus the either/or rule with `--with`.
- `README.md`: a new row in the commands table.
- `tests/`: unit tests for parsing and splitting, and CLI tests for a full split, a total that isn't 100, and combining `--with` with `--percent`.