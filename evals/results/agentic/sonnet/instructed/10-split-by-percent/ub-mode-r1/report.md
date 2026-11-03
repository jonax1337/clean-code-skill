`tabtally add` now takes `--percent NAME=PCT`, so `--percent alice=50 --percent bob=30 --percent carol=20` splits an expense by percentage. All 46 tests pass, including the new ones. I committed it locally as `79fd425` but didn't push, and I didn't run the crapper, dryer or mutator tools.

- **Either/or with `--with`:** `--with` and `--percent` can't be combined, and `add` needs one of them.
- **Validation:** the percentages must be whole numbers and add up to 100. A person listed twice, or a spec that isn't `NAME=PCT`, is rejected. A rejected `add` exits with code 2 and saves nothing.
- **Cents:** leftover cents are handled by the existing rounding, so the shares always add up to the full amount.
- **Where the change is:** the parsing and checks are in `tabtally/splitting.py`, the option is wired in `tabtally/cli.py`, and I added a README row for it.

The tests I added cover the split, cent handling, the rejection cases and the CLI behaviour.

Log:
- I loaded ub-mode and read `cli.py`, `splitting.py`, `money.py` and the existing tests.
- I wrote the failing tests first and confirmed they failed on the missing `split_by_percent`.
- I implemented it, ran the suite, then updated the README and committed.