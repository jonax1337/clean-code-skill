`tabtally add` now takes `--percent NAME=PCT`, so you can split an expense by percentage instead of equally.

```console
$ python -m tabtally add --paid-by alice --amount 100.00 --description Rent --percent alice=50 --percent bob=30 --percent carol=20
```

**How it works**
- **`tabtally/splitting.py`:** a new `split_by_percent(cents, [(name, pct), ...])` function. It rejects a name listed twice, negative percentages, and totals other than 100, and the error message shows the wrong total. The actual split goes through the existing `allocate`, so the shares still add up to the exact amount. For example, 10.01 split 50/30/20 gives 5.01 / 3.00 / 2.00. I moved the duplicate-name check into a small helper so both split functions use it.
- **`tabtally/cli.py`:** `--with` and `--percent` are now an either/or pair, and one of them is required. Using both, or neither, is a usage error. Input that isn't `NAME=<whole number>` (like `alice`, `=50`, `alice=12.5` or `alice=5x`) is rejected with a usage message. Percentages that don't add up to 100 give the same `error: ...` message and exit code 2 as a bad amount, and nothing is saved.
- **`README.md`:** the commands table now includes the `--percent` form.

**Two choices you may want to change**
- A 0% share is allowed. That person is recorded with a share of 0.00.
- Combining the two options (some people equal, some by percent) isn't supported, because it's not clear what that should mean.

**Checks:** `python -m pytest` gives 49 passed: the original 34, plus 15 new tests for the splitting rules and the CLI behaviour, which failed before the change. I also ran the CLI by hand for a valid percentage split and a malformed `--percent`, and both behaved as described above. The project doesn't have a linter or type checker set up, so I didn't run one.

I haven't committed anything.