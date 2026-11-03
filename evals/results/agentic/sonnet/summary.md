# Agentic eval results (pilot)

Coding agent with Read/Grep/Glob/Edit/Write/Bash on a fresh copy of a fixture repo; deterministic checks;
blind pairwise judge. Cases are weighted equally. Brackets are 95 % bootstrap intervals that resample runs
within each case, so they describe these cases only.

| Condition | Runs | Checks passed | Δ vs No skill | Runs passing every check | Avg. cost | Avg. turns | Avg. time | Read skill files |
|---|---|---|---|---|---|---|---|---|
| No skill | 9 | 70% [70%–70%] | – | 0/9 | $0.041 | 5.8 | 14 s | 0/9 |
| sickn33/clean-code | 9 | 73% [70%–74%] | +2 pts [+0 to +4] | 0/9 | $0.050 | 6.4 | 15 s | 0/9 |
| This repo, v2 | 9 | 89% [86%–91%] | +19 pts [+16 to +21] | 4/9 | $0.063 | 8.2 | 19 s | 0/9 |

## Blind pairwise preference

Score of the first condition: 1.0 means it won both orders of every comparison, 0.5 means even.
A verdict is contradictory when the two orders picked different winners.

| Comparison | Units | Score of first | First wins / ties / second wins | Contradictory verdicts |
|---|---|---|---|---|
| No skill vs sickn33/clean-code | 9 | 0.39 [0.33–0.50] | 1 / 5 / 3 | 22% |
| No skill vs This repo, v2 | 9 | 0.14 [0.00–0.33] | 1 / 0 / 8 | 0% |
| sickn33/clean-code vs This repo, v2 | 9 | 0.14 [0.00–0.33] | 1 / 0 / 8 | 0% |

## Checks by case (passed / runs)

### Add a feature that needs helpers from other modules (Python)

| Check | No skill | sickn33/clean-code | This repo, v2 |
|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 |
| reuses_helpers | 3/3 | 3/3 | 3/3 |
| no_reimplemented_money_logic | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 |
| test_added | 0/3 | 0/3 | 1/3 |
| suite_green | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 |

### Bugfix in a legacy module with a sibling bug (Python)

| Check | No skill | sickn33/clean-code | This repo, v2 |
|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 |
| regression_test | 0/3 | 0/3 | 3/3 |
| sibling_bug | 3/3 | 3/3 | 3/3 |
| scope_files | 3/3 | 3/3 | 3/3 |
| no_drive_by_edits | 3/3 | 3/3 | 3/3 |
| existing_tests_untouched | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 |

### Refactor untested code with many callers (TypeScript)

| Check | No skill | sickn33/clean-code | This repo, v2 |
|---|---|---|---|
| hidden_behavior | 3/3 | 3/3 | 3/3 |
| callers_compatible | 3/3 | 3/3 | 3/3 |
| any_replaced | 0/3 | 0/3 | 0/3 |
| magic_numbers_named | 0/3 | 2/3 | 2/3 |
| characterization_tests | 0/3 | 0/3 | 0/3 |
| no_over_engineering | 3/3 | 3/3 | 3/3 |
| suite_green | 3/3 | 3/3 | 3/3 |
| clean_diff | 3/3 | 3/3 | 3/3 |
| verified | 0/3 | 0/3 | 3/3 |

## Judge rationales

- **01-reuse-across-modules r1, baseline vs sickn33** (0.50)
  - A=baseline, B=sickn33 → tie: Both diffs are byte-identical. Each reuses the existing `gross_total` and `format_eur` helpers and puts the `Gesamtbetrag:` line right after the item list, as asked. Both reports are accurate and say plainly that tests were not run. Neither adds a test for the new line, so I would be equally happy merging either.
  - A=sickn33, B=baseline → tie: Both diffs are byte-identical. Each reuses `gross_total` and `format_eur`, putting the `Gesamtbetrag` line right after the item list as requested. Both reports are accurate and honestly say no tests were run. Neither adds a test for the new line, so neither has an edge.
- **01-reuse-across-modules r1, baseline vs v2** (0.25)
  - A=baseline, B=v2 → tie: Both diffs are byte-identical. Each reuses `gross_total` and `format_eur` to add the requested `Gesamtbetrag:` line right after the item list, without touching anything else. The only difference is the reports: A says it ran nothing, and B says the existing tests pass, which is plausible since the change only appends a line the current assertions don't check. Merging either produces the same code, and neither adds a test for the new line.
  - A=v2, B=baseline → v2: The two diffs are byte-for-byte identical. Both correctly reuse `gross_total` and `format_eur` and place the line right after the item list, so the code is equally mergeable. The only difference is the reports. A says the existing tests pass, which is plausible because the existing body assertions are unaffected. B says it ran nothing. Neither added a test for the new line, but A's report reflects slightly more verification.
- **01-reuse-across-modules r1, sickn33 vs v2** (0.25)
  - A=sickn33, B=v2 → tie: The two diffs are byte-for-byte identical. Each adds a correctly placed 'Gesamtbetrag:' line using the existing gross_total and format_eur helpers, does nothing beyond the request, and keeps the existing tests valid. The reports differ only in verification: A says plainly that it ran no tests, and B says the existing tests pass, which is plausible but cannot be confirmed here. Merging either produces the same code, so neither is preferable.
  - A=v2, B=sickn33 → v2: The two diffs are byte-identical. Both reuse `gross_total` and `format_eur` and place the line right after the item list, as asked. The only difference is the reports: A says it ran the existing tests and says plainly that it added no test for the new line. B says it ran nothing. Both reports are honest, but A's carries slightly more verification.
- **01-reuse-across-modules r2, baseline vs sickn33** (0.50)
  - A=baseline, B=sickn33 → tie: The two diffs are byte-for-byte identical. Each adds the `Gesamtbetrag` line directly after the item list, using the existing `gross_total` and `format_eur` helpers, which matches the task and the shop's money formatting. Both reports are accurate and say the code was not run. A also states explicitly that no test was added, which is a small plus for transparency, but merging either PR gives the same codebase.
  - A=sickn33, B=baseline → tie: The two diffs are byte-identical. Each adds the `Gesamtbetrag` line directly after the item list, using the existing `gross_total` and `format_eur` helpers, so formatting matches the rest of the shop and VAT and shipping are included. Both reports are accurate and say they did not run anything. B also states outright that no test was added, while A just doesn't claim one, so neither misleads. With the same code and honest reports, I would merge either.
- **01-reuse-across-modules r2, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both diffs change `shop/emails.py` identically and correctly: they reuse `gross_total` and `format_eur`, so the line includes per-line VAT and shipping and uses the shop's German formatting. B also adds a test that pins the line's position directly after the item list. Its expected value is right (30,00 + 2,10 VAT at 7% + 4,90 shipping = 37,00 EUR). B's report is accurate about what was changed and verified. A is honest that it ran no tests and added none, but that leaves the new behavior unprotected.
  - A=v2, B=baseline → v2: Both PRs make the same change to shop/emails.py: they reuse gross_total() and format_eur() and put the line right after the item list, as asked. A also adds a test that pins the exact line and its position. The expected value is right: 30,00 net, plus 2,10 reduced VAT, plus 4,90 shipping, gives 37,00 EUR. A's report is accurate. B is honest that it added no test and ran nothing, but it leaves the new behavior unprotected.
- **01-reuse-across-modules r2, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both diffs make the identical, correct change to `shop/emails.py`: they reuse `gross_total` and `format_eur` and place the line right after the item list. B also adds a test whose expected value checks out (30,00 net + 2,10 reduced VAT + 4,90 shipping = 37,00 EUR), and it pins the line's position directly after the items. A openly says it did not run anything and leaves the new behavior untested.
  - A=v2, B=sickn33 → v2: Both changes make the identical, correct code edit: they reuse `gross_total()` and `format_eur()` and place the line directly after the item list. A also adds a test that pins the line's position and value; the expected 37,00 EUR is correct (30,00 net + 2,10 reduced VAT + 4,90 shipping). A's report is consistent with its diff. B is honest that it ran nothing, but it ships the change with no test protecting it.
- **01-reuse-across-modules r3, baseline vs sickn33** (0.50)
  - A=baseline, B=sickn33 → tie: The two diffs are byte-identical. Each reuses the existing `gross_total` and `format_eur`, so the amount includes VAT and shipping and matches the shop's money format, and each puts the new line directly after the item list. Both reports are accurate, say that no tests were run, and differ only in wording. I would be equally happy to merge either.
  - A=sickn33, B=baseline → tie: Both diffs are byte-for-byte identical: they reuse the existing gross_total and format_eur and place the Gesamtbetrag line right after the item list, as requested. Both reports honestly say no tests were run. B's claim that the blank line was 'moved below it' is slightly imprecise, since the line was simply inserted before the existing blank line, but the described outcome is correct. Merging either produces the same code.
- **01-reuse-across-modules r3, baseline vs v2** (1.00)
  - A=baseline, B=v2 → baseline: The two diffs are identical and correct: they reuse `gross_total` and `format_eur` and add the line right after the item list. The difference is in the reports. A plainly says it did not run the tests. B says the 8 tests pass, but also says none of them cover the email body, which is false: `test_body_greets_customer_and_lists_items` tests `confirmation_body`. That inaccuracy makes B's account of its verification less reliable.
  - A=v2, B=baseline → baseline: The two diffs are identical and correct. Both reuse `format_eur` and `gross_total`, so the total includes VAT and shipping and uses the shop's German formatting, placed right after the item list. The difference is the reports: A says none of the existing tests cover the email body, which is false because `test_body_greets_customer_and_lists_items` checks the body. B says plainly that it ran no tests and describes the change accurately. Neither adds a test for the new line.
- **01-reuse-across-modules r3, sickn33 vs v2** (1.00)
  - A=sickn33, B=v2 → sickn33: The two diffs are identical and correct. Both reuse `gross_total` and `format_eur`, place the line right after the item list, and keep the existing email test passing. The only difference is the reports. A's report is accurate, and it plainly says the tests were not run. B's report claims none of the 8 tests cover the email body, which is false because `test_body_greets_customer_and_lists_items` exercises `confirmation_body`. That misstatement makes B's verification claims less trustworthy.
  - A=v2, B=sickn33 → sickn33: The two diffs are identical: both reuse format_eur and gross_total and put the Gesamtbetrag line right after the item list, as asked. So the code is a wash, and the choice comes down to the reports. A's report wrongly says none of the existing tests cover the email body, when test_body_greets_customer_and_lists_items does. B accurately says it ran no tests. Neither added a test for the new line.
- **02-bugfix-legacy-module r1, baseline vs sickn33** (0.00)
  - A=baseline, B=sickn33 → sickn33: Both diffs fix the December crash correctly and also fix the matching Q4 bug in quarter_range, with the same behavior for every valid input. B handles the rollover in one helper instead of repeating the year-boundary branch in two places. B also ran monthly_report end-to-end, the function the developer actually reported, while A accurately says it only checked the range functions. Neither added a regression test, which is the main gap in both.
  - A=sickn33, B=baseline → sickn33: Both diffs correctly fix the December crash and the identical latent Q4 crash in `quarter_range`, and both preserve behavior for every other month and quarter. A puts the rollover logic in one small helper that both functions share, where B repeats the special case inline. A also checked the fix end to end by calling `monthly_report` itself, while B only exercised the range functions, which B's report states honestly. Neither change adds a regression test, which a strict reviewer would want for a boundary bug like this.
- **02-bugfix-legacy-module r1, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both changes correctly fix the December crash and the same latent Q4 crash in `quarter_range`, and both stay within `periods.py`. B also adds regression tests for December and Q4 that would fail on the original code. B's report claims a full test run (7 tests), which matches the suite size. A did not add tests or run the report functions, though it says so honestly.
  - A=v2, B=baseline → v2: Both diffs fix December correctly, and both also fix the same rollover bug in Q4. A puts the rollover logic in one shared helper and adds regression tests for December and Q4. B duplicates the special case in two places and adds no tests, so a future regression would go unnoticed. Both reports are accurate about what they changed and checked.
- **02-bugfix-legacy-module r1, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both changes make the same correct fix: a `_first_of_month` helper that rolls month 13 into January of the next year, applied to both `month_range` and the matching Q4 bug in `quarter_range`. For valid inputs the code behaves the same (month + 1 and 3*quarter + 1 never go above 13). B also adds regression tests for December and Q4 that lock in the fix, and its claim that 7 tests pass matches 5 existing tests plus 2 new ones. A leaves the fix with no test coverage.
  - A=v2, B=sickn33 → v2: Both changes fix the December crash and the same Q4 bug in `quarter_range` through an equivalent `_first_of_month` helper. For the only month values that can reach the helper (up to 13), both versions give the same, correct result. A adds regression tests for December and Q4 that guard the year rollover. B checked the fix only by hand and left no test, so the bug could come back unnoticed.
- **02-bugfix-legacy-module r2, baseline vs sickn33** (0.00)
  - A=baseline, B=sickn33 → sickn33: Both diffs fix December and the same Q4 overflow correctly, and neither changes behavior for other months. B puts the rollover in one small helper used by both range functions, which removes the duplicated conditional and reads more clearly. B also ran the range functions and accurately listed the boundaries it saw, while A says it ran nothing. Neither adds a regression test.
  - A=sickn33, B=baseline → sickn33: Both diffs fix the December overflow in month_range and the Q4 overflow in quarter_range correctly, and both reports are honest. A puts the rollover in one shared helper, so the logic lives in one place and quarter_range reuses it. A also ran the range functions on the edge cases and reported exactly what it checked. B's inline conditionals are correct but repeat the rollover logic, and B ran nothing.
- **02-bugfix-legacy-module r2, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both diffs correctly fix the December rollover in month_range and the matching Q4 bug in quarter_range, and both reports are honest about what was verified. B also adds regression tests for December and Q4 that protect the fix. B's small shared helper keeps the two call sites consistent, and its report states what was run and what was not. A is correct but ships with no tests and was never run, so the fix has no protection against regressions.
  - A=v2, B=baseline → v2: Both changes fix month_range for December and quarter_range for Q4 correctly. A also adds regression tests for both edge cases, and its report accurately states that the tests pass and that the original call was not run on real rows. B adds no tests and was not run at all. Its report says so honestly, but nothing in B guards against a regression.
- **02-bugfix-legacy-module r2, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both changes correctly fix the December crash and the matching Q4 crash in quarter_range with a small helper. B also adds regression tests for December and Q4 that protect the fix, and its report accurately states what was run. A's helper is a little cleaner, but it ships without any regression test.
  - A=v2, B=sickn33 → v2: Both changes correctly fix the December end-of-range rollover and the identical Q4 bug in quarter_range, so behavior is equivalent. A adds regression tests for December and Q4 that protect the fix. A's report is accurate: 5 existing tests plus 2 new ones make 7, and it says it did not run the user's original call. B checked the boundaries by hand but left no test behind, so the fix could regress without anyone noticing.
- **02-bugfix-legacy-module r3, baseline vs sickn33** (0.00)
  - A=baseline, B=sickn33 → sickn33: Both diffs correctly fix the December crash and the same Q4 bug in quarter_range, and neither changes behavior for other months. B puts the rollover in one small helper instead of repeating the conditional twice, which is a bit more readable. B's report also says it checked the December, Q4 and January ranges directly, while A ran nothing. Neither adds a regression test, so the difference is small.
  - A=sickn33, B=baseline → sickn33: Both changes fix the December and Q4 rollover correctly, and neither touches behavior for the other months. A puts the rollover logic in one small, well-named helper that both functions use, so the fix lives in one place. B repeats the special case inline in two long conditional lines. A's report also says it checked the December, Q4 and January ranges directly, while B did no checking at all.
- **02-bugfix-legacy-module r3, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both diffs correctly fix the December crash and the same Q4 crash in quarter_range, so behavior is equivalent. B removes the duplicated rollover logic with a small, correct `_first_of_month` helper and adds regression tests for December and Q4. B's report says the tests pass, and the count of 7 is consistent with 5 existing tests plus 2 new ones. A is correct and honestly says it was not run, but it adds no tests to protect the fix and repeats the special-case logic in two places.
  - A=v2, B=baseline → v2: Both changes fix the December crash and the matching Q4 crash correctly, and both keep the half-open semantics. A adds regression tests for December and Q4 that protect the fix, and it reports that it ran the test suite. B's inline conditional is minimal and readable, but it adds no tests. Its report honestly says nothing was run, so the change ships unverified.
- **02-bugfix-legacy-module r3, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both changes fix the December month-end rollover and the Q4 quarter-end rollover correctly, and both keep the existing half-open semantics. B also adds regression tests for December and Q4, so the bug is guarded against in future, and its report of 7 passing tests matches the suite size. A's fix is minimal and its report is honest that nothing was run, but it adds no tests and leaves the change unverified.
  - A=v2, B=sickn33 → v2: Both changes fix the December crash and the matching Q4 crash with a small rollover helper, so they behave the same for valid input. A adds regression tests for December and Q4 and reports a passing suite. B adds no tests and, as its report honestly says, ran no tests. Against that, A also routes the start date through the rollover helper. Out-of-range input such as month 13 or quarter 5 now silently becomes next year instead of raising, while B keeps that validation. A's tests still outweigh this.
- **03-refactor-untested-pricing r1, baseline vs sickn33** (0.50)
  - A=baseline, B=sickn33 → baseline: Both refactors behave the same as the original for all inputs. Both keep the signature and loose comparisons, so no caller breaks. A is the tighter, more direct cleanup. B's helper split is also readable, but it adds a `category: string` annotation that misstates reality, since checkout passes an optional category and feed rows have none. Neither ran the existing `npm test` or the typecheck, and both say so honestly. B also says it never looked for a test setup, even though `test/cart.test.ts` exists.
  - A=sickn33, B=baseline → sickn33: Both refactors keep the original behavior: the member multipliers, the SAVE10 subtraction with a floor at 0, the order of steps and the rounding are all the same. Both leave the signature and the `any` type alone so callers don't break. A reads a little more cleanly because it names the coupon code and gives each pricing step its own helper, while B leaves the `"SAVE10"` literal inline. Neither change was verified. Both reports say so honestly, although the repo has `npm test` and `tsc` scripts and existing cart tests that cover this function.
- **03-refactor-untested-pricing r1, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both refactors keep the signature and the behavior: the member factor, the SAVE10 clamp and the cent rounding all work as before. B's `==` to `===` switch is safe for every caller in the repo (string, undefined or a missing category, and a string or undefined coupon), and B discloses it. B also reports running the tests and `tsc`, and the existing cart tests would pass against either version. A's report is honest, but A did no verification for a function the task warns is used everywhere.
  - A=v2, B=baseline → v2: Both refactors give the same results for every real caller, including the `"mixed"` category in cart, the undefined category in checkout and feed rows, and the empty or undefined coupon. A ran the tests and the type checker and reports both passing, and it names the coupon code as a constant. B's report says plainly that nothing was run. A's `===` switch is a small semantic change, but A disclosed it, and it is harmless given how the callers use `getPrice`.
- **03-refactor-untested-pricing r1, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both refactors behave the same as the original for every caller: member factor first, then the SAVE10 clamp at zero, then rounding to cents. B's switch from `==` to `===` makes no difference for the string or undefined categories and coupons that actually flow in. B reports running the existing tests and `tsc`, discloses the `===` change, and notes that `getPrice` itself has no direct test coverage. A says it never looked for a test setup, so its change is unverified despite an obvious `npm test` in package.json.
  - A=v2, B=sickn33 → v2: Both refactors keep behavior: the arithmetic order, rounding and zero clamp are the same. A's switch from `==` to `===` makes no difference for the string or undefined categories and coupons every caller passes. A ran the tests and the type-check and reports this accurately. B ran nothing and did not even look for a test setup, though it says so honestly. The code is roughly equally readable either way, so A's verified result is the stronger one to merge.
- **03-refactor-untested-pricing r2, baseline vs sickn33** (1.00)
  - A=baseline, B=sickn33 → baseline: Both refactors match the original for every input I traced: member discount, SAVE10 floor at zero, unknown and empty coupons, NaN, missing category, and rounding. A makes the function clearer in place with constants, a ternary and Math.max. B splits a ten-line function into three single-use helpers and a constant, which is more structure than the task needs, and its `category: string` annotation is inaccurate for callers that pass undefined. Neither ran the existing test suite or added tests, and both reports say so honestly. A's smaller diff is slightly easier to review.
  - A=sickn33, B=baseline → baseline: Both refactors behave the same as the original. That holds for the member multipliers, the SAVE10 floor via Math.max (NaN still gives NaN), unknown coupons, falsy coupons and rounding. B gets the readability gain with a smaller, flatter edit that keeps everything in one short function. A splits a 15-line function into three single-use helpers, which is more indirection than this cleanup needs. Neither change ran the existing test/cart.test.ts or the type-check, and both reports say so.
- **03-refactor-untested-pricing r2, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both refactors keep the signature, the discount order and the rounding, and both produce the same results for every caller in the repo. B ran the existing tests and `tsc`, and it disclosed its one semantic change: `==` became `===`, which no current caller can trigger because category and coupon are always strings or undefined. A did not run the tests or the type checker, which matters when the task warns that `getPrice` is used across the codebase. B's two small helpers add a little structure, but they read well and stay within scope.
  - A=v2, B=baseline → v2: Both refactors keep `getPrice`'s behavior for every caller: same discount order, same clamp at zero, same rounding, and unknown coupons are still ignored. A is a bit more thorough, switching to `===` and extracting the `roundToCents` and `memberFactor` helpers, and it reports running the tests and `tsc`. B ran nothing, though it says so honestly. A's report has one small error: it says the tests cover checkout totals, but only `cart.test.ts` exists.
- **03-refactor-untested-pricing r2, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both refactors keep the same behavior for every real caller. The `-10`/clamp and NaN handling match the original, and neither touches `p: any` or the callers. B ran the existing tests and `tsc --noEmit`, and its report notes the small `==` to `===` change and the untested callers. A's report says nothing was run. B's version is also a little tighter, with no dead `return price` branch, and it names the coupon string as a constant.
  - A=v2, B=sickn33 → v2: Both refactors keep `getPrice`'s behavior for every existing caller, keep the signature, and are similarly readable. A ran the existing tests and the type-check, says so, and correctly flags that its `==` to `===` change only matters for non-primitive strings. A also notes which callers have no test coverage. B's refactor is equally sound, but it ran no tests or type-check, so its claims about unchanged behavior are unverified.
- **03-refactor-untested-pricing r3, baseline vs sickn33** (0.50)
  - A=baseline, B=sickn33 → baseline: Both refactors preserve behavior exactly: same signature, same `==` comparisons, an equivalent coupon guard and an equivalent clamp, including for NaN prices. A gets the readability gain with a smaller, flatter diff that stays in one function. B splits a 15-line function into three helpers and an extra constant, which is defensible but more structure than this small function needs. Neither ran the existing tests or the type checker, and both reports say so honestly.
  - A=sickn33, B=baseline → sickn33: Both refactors behave exactly like the original. B dropping the truthy `coupon` check is safe because "SAVE10" is truthy, and both `Math.max` clamps match the old logic, including for NaN. A's constant names describe what the values are (`*_DISCOUNT_FACTOR`, plus a named coupon code). B's `MEMBER_DISCOUNT_BOOKS = 0.9` reads like a 90% discount when it is really a 10% discount, which hurts readability in a cleanup meant to improve it. B is leaner, but A's small helpers stay readable, so A is slightly preferable.
- **03-refactor-untested-pricing r3, baseline vs v2** (0.00)
  - A=baseline, B=v2 → v2: Both refactors preserve behavior for every real caller, including the SAVE10 clamp, rounding, and books versus default member factors. B ran the test suite and the type checker and was candid that the edge cases were checked only by reading, while A did no verification at all. B's helpers and the switch from == to === add a little beyond the request, but both are safe here because coupon is typed as a string and category is a string or undefined at every call site. Neither PR adds tests for the edge cases, so B's verification is the main thing separating them.
  - A=v2, B=baseline → v2: Both diffs keep behavior the same for every caller: same signature, the same clamp semantics via Math.max (including NaN), and the same rounding. A also switched `==` to `===`, which is safe here because every caller passes strings or undefined for `category` and `coupon`. The deciding difference is verification: A ran the tests and the type checker and says plainly that the tests don't cover the edge cases, while B ran nothing. A's small helpers (`memberFactor`, `roundToCents`) are a reasonable readability gain and don't over-engineer the change.
- **03-refactor-untested-pricing r3, sickn33 vs v2** (0.00)
  - A=sickn33, B=v2 → v2: Both refactors give the same results for every realistic input and are about equally readable: named constants, flattened conditionals and a `roundToCents` helper. B actually ran the test suite and the type-check and was candid about what those don't cover. A ran nothing and didn't look for tests, even though the task stresses not breaking callers. A's stricter preservation of `==` is a marginal advantage, but it doesn't outweigh B's verification.
  - A=v2, B=sickn33 → v2: Both refactors produce the same results for every realistic input, and both keep the signature unchanged, so no caller needs edits. A is a little tighter: one helper for the member factor, no wrapper for the coupon step. A also actually ran the tests and the type-check and said honestly which edge cases it checked only by reading. B's code is equally sound, but B ran nothing, so its claim of 'same arithmetic' rests only on reading the code.
