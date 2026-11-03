`tabtally add` now accepts `--percent NAME=PCT`, and all 50 tests pass. The change is committed on `main` as `446e4de`, but I couldn't push it because the repo has no remote.

```console
$ python -m tabtally add --paid-by alice --amount 10.00 --description Taxi --percent alice=50 --percent bob=30 --percent carol=20
added #1: 10.00 for Taxi
$ python -m tabtally balances
alice 5.00
bob -3.00
carol -2.00
```

**How it behaves**
- **`--with` or `--percent`:** you must give one of them, and you can't use both in the same command. Breaking either rule gives a normal usage error (exit code 2).
- **Input checks:** each value must be `NAME=` followed by a whole number. Inputs like `alice`, `=50`, `alice=12.5`, `alice=-5` and `alice=abc` are rejected with `error: ...`, and nothing is saved.
- **Rules for the percentages:** they must add up to exactly 100, and the error says what they actually added up to. Each person's percentage must be above zero, and the same name can't appear twice.
- **Odd cents:** rounding uses the same rule as equal splits, so the shares always add up to the full amount. For example, 10.01 split 50/50 becomes 5.01 and 5.00.

**Decision for you:** I made 0% an error, since it would add a person who owes nothing. If you'd rather allow it, it's a one-line change in `tabtally/splitting.py`.

**Log**
1. Read the code. Equal splits already go through `money.allocate`, which divides by weights and never loses a cent. That made percentages a simple case of the same thing: the percentages are the weights.
2. Wrote the tests first: 5 for the splitting logic and 5 for the command line, with two of them each covering several inputs. Ran them and they failed as expected, because `split_by_percent` didn't exist yet.
3. Added `split_by_percent` to `tabtally/splitting.py`. Moved the duplicate-name check into one helper that both kinds of split use, so it isn't written twice.
4. In `tabtally/cli.py`, made `--with` and `--percent` alternatives (one required) and turned each `NAME=PCT` into a name and a number as soon as it's read.
5. My edit script had written `cli.py` with Windows line endings, so I changed it back to Unix ones.
6. The crapper, dryer and mutator tools the skill calls for aren't installed. Instead I checked by hand that each new function is small and that the tests reach each of its branches.
7. Added the new option to the command table in `README.md`, then committed with a message giving why, what changed, and the test results.