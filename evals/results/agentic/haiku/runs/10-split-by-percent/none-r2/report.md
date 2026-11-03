`tabtally add` now takes `--percent NAME=PCT`, and the 52 tests pass, including new ones for the percentage path.

```
python -m tabtally add --paid-by alice --amount 100 --description Rent --percent alice=50 --percent bob=30 --percent carol=20
```

Changes:

- **`tabtally/cli.py`**: `--with` and `--percent` are now a required mutually exclusive pair, so one split style must be given and not both. Parsing and splitting happen in `_add`.
- **`tabtally/splitting.py`**: added `parse_percent` (reads `NAME=PCT`) and `split_by_percent` (checks duplicates and that the total is 100). Shares come from the existing `allocate`, so odd cents still go to someone and the total always matches the amount. The duplicate check moved into a shared helper that `split_equally` also uses.
- **`tests/`**: CLI tests cover a clean split, cent rounding, totals not equal to 100, a bad value, and the `--with`/`--percent` conflict. Unit tests cover parsing and the split itself.
- **`README.md`**: added a row for the new form to the commands table.

Choices I made that you may want to change:

- Each percentage must be a whole number from 1 to 100. A `0` is rejected, so a person with no share has to be left off the list.
- Errors go through the existing `MoneyError` path, so they print `error: ...` and exit with code 2, like the other add failures.

I haven't committed anything.