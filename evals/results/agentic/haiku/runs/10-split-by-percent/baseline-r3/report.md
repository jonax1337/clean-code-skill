`tabtally add` now takes `--percent NAME=PCT`, and the full suite passes (52 tests). I haven't committed anything.

```
python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
```

- **Either/or:** `--with` and `--percent` are a required mutually exclusive pair, so an expense uses one or the other.
- **Validation:** Each percent must be a whole number from 1 to 100, and the total must be exactly 100. Otherwise the command exits with status 2 and saves nothing. Duplicate names are rejected, as with `--with`.
- **Rounding:** Splitting reuses the existing `allocate` function, so shares always add up to the full amount in cents.
- **Changed files:** `tabtally/splitting.py` gets `split_by_percent`, and the duplicate check moved there as a shared `reject_duplicates`. `tabtally/cli.py` gets the parser change, and `README.md` documents the option. Tests are in `tests/test_splitting.py` and `tests/test_cli.py`.

Choices I made that you may want to change:
- **Zero percent is rejected.** A person with 0% is probably a mistake, so I required at least 1. Allowing 0 is a one-line change in `_parse_percent`.
- **Test fixture change:** The `run` fixture in `tests/test_cli.py` now catches `SystemExit`, because argparse exits that way on usage errors. The production code is unaffected.