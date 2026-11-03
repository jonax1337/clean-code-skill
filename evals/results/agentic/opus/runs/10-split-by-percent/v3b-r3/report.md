`tabtally add` now takes `--percent NAME=PCT`, so an expense can be split by percentage. `python -m pytest` passes (48 tests, 14 of them new), and I ran the CLI by hand once: `alice=50 bob=40` printed `error: percentages must add up to 100, not 90` and exited with code 2.

**How it works**
- **`tabtally/splitting.py`:** the new `split_by_percent` function reads each `NAME=PCT` entry, checks that the percentages total 100, and hands them to the existing `allocate` function as weights. Every cent is still accounted for, so 10.01 split 50/30/20 becomes 5.01 / 3.00 / 2.00. I moved the duplicate-name check into a small helper so the equal split and the percentage split share it.
- **`tabtally/cli.py`:** `--with` and `--percent` are now alternatives. You must give one of them, and argparse rejects a command that uses both.
- **Invalid input:** a missing name, a missing percentage, a decimal (`12.5`), text, a negative number or `0` is rejected with a clear message. So are a name listed twice and a total other than 100. These go through the same error path as other usage errors (exit code 2), and nothing is saved.
- **README:** added a line for the new form of `add`.

**One choice for you:** I reject `0%` entries, because someone with a 0% share doesn't need to be listed. If you want to allow them, change `int(percent) <= 0` to `< 0` in `_parse_percent`.

I haven't committed anything.