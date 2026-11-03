`tabtally add` now takes `--percent NAME=PCT`, and all 49 tests pass (34 existing, 15 new). I didn't commit.

```
$ python -m tabtally add --paid-by alice --amount 100.00 --description Groceries --percent alice=50 --percent bob=30 --percent carol=20
added #1: 100.00 for Groceries
$ python -m tabtally balances
alice 50.00
bob -30.00
carol -20.00
```

**What changed**
- **`tabtally/cli.py`**: `--with` and `--percent` form a required mutually exclusive group, so `add` needs exactly one of them. `_parse_percent` turns `NAME=PCT` into a name and a whole number. Anything else (no `=`, empty name, `50.5`, `-10`, `fifty`) is reported as `error:` with exit code 2, and nothing is saved.
- **`tabtally/splitting.py`**: new `split_by_percent`. It rejects a name listed twice, and rejects totals other than 100 with a message such as "must add up to 100, not 90". It shares the duplicate check with `split_equally`, and splits the amount with the existing `allocate`, so cents are never lost.
- **`README.md`**: documented the new form in the commands table.
- **Tests**: split logic, rounding with odd cents, bad totals, duplicates, malformed input, and the `--with`/`--percent` conflict.

**Choices I made**
- A percentage of `0` is accepted, meaning that person owes nothing. Say if you'd rather reject it.
- Rounding follows the existing rule: leftover cents go to the largest remainders, earlier people first on a tie. So `34/33/33` on 10.00 gives 6.60, 3.30, 3.30.
- Using `--with` together with `--percent`, or neither, is an argparse usage error (exit code 2), the same as other missing required options.