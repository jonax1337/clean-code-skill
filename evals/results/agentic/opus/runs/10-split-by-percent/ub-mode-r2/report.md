`tabtally add` now takes `--percent NAME=PCT`. I committed it to `main` as `dee933a`. All 50 tests pass, and I ran the command by hand to check it:

```console
$ python -m tabtally add --paid-by alice --amount 30.00 --description Pizza --percent alice=50 --percent bob=30 --percent carol=20
added #1: 30.00 for Pizza
$ python -m tabtally balances
alice 15.00
bob -9.00
carol -6.00
```

**How it behaves**
- You use either `--with` or `--percent`, never both, and one of them is required. Passing both gives `argument --percent: not allowed with argument --with`.
- Each percentage must be a whole number: digits only, with no sign, decimal point or negative value. The name can't be empty. A value that breaks these rules (e.g. `alice=12.5` or `=50`) stops the command with exit code 2 and nothing is saved.
- If the percentages don't add up to 100 you get `error: percentages must add up to 100, not 99`, exit code 2, and nothing is saved.
- Every cent is kept: 10.01 split 50/30/20 gives 5.01, 3.00 and 2.00. Leftover cents are handed out by the existing `allocate` function in `money.py`.
- A 0% share is allowed. That person is recorded with a 0.00 share.
- The README's command table now covers the new option.

**Log**
1. Read the code. `money.allocate` already splits by weight, so percentages just become the weights and no new rounding code was needed.
2. Wrote the splitting tests first and saw them fail on the missing import.
3. Added `split_by_percent` in `splitting.py`, which checks that the total is 100. Both kinds of split now go through one `_split` helper, so the check for a name listed twice lives in one place.
4. Wrote the command-line tests. The ones for bad input and for using both flags were passing for the wrong reason (`--with` was still required), so I made them check the error text. After that they failed as they should.
5. Added the `--percent` option in `cli.py`. A `NAME=PCT` value is checked when the arguments are read, and from then on it's a `(name, int)` pair.
6. Ran the whole test suite and tried the command by hand.
7. Updated the README and made one commit.

**Skipped**
- **Code-quality tools:** the skill asks for the `crapper`, `dryer` and `mutator` tools, but none of them are installed here, so I didn't run them. The new functions are short and branch very little.
- **Push:** the repo has no remote, so I committed locally but couldn't push.