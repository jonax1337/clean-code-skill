`tabtally add` now takes `--percent NAME=PCT`. For example, `--percent alice=50 --percent bob=30 --percent carol=20` splits the expense 50/30/20. The full test suite passes (41 tests), including the new ones.

- **Rules:** percentages must be whole numbers and must add up to 100. A name can only appear once. A malformed value like `bob` or `bob=50.5` is rejected.
- **Rounding:** leftover cents are handled the same way as the equal split, so the shares always add up to exactly the amount.
- **`--with` and `--percent`:** `--with` is no longer required on its own. You must give either `--with` or `--percent`, and giving both or neither is an error. Errors print `error: …` and exit with code 2, and nothing is saved.
- **Code:** the new split logic is in `tabtally/splitting.py` and the option is in `tabtally/cli.py`.
- **Tests:** I added a percent-split test and tests for the rejected inputs in `tests/test_cli.py`.

I haven't committed anything or updated the README.