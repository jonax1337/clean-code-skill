I've added `test/rates.test.ts` with 38 tests for `src/rates.ts`. All 38 pass, and `npm run typecheck` reports no errors. I didn't touch `src/rates.ts`.

The tests cover:
- **`minorUnitsOf`:** the minor units of every currency, rejection of unknown or wrongly cased codes, and the currency on the `UnknownCurrencyError`.
- **`convert`:** same-currency conversion, the euro rates, conversions between currencies with different minor units, zero and negative amounts, and rejection of non-integer, non-finite or unsafe amounts and unknown currencies.
- **Rounding:** ties go away from zero for the half-up currencies (USD, JPY) and to the even neighbor for the half-even ones (EUR, CHF, KWD). I included negative ties, and checked that the target currency's mode is the one used.
- **`feeFor`:** zero amounts, the 2.5% rate, the minimum and maximum fees (including amounts that land exactly on a limit), fee ties under each rounding mode, and rejection of negative, invalid or unknown-currency input.
- **`quote`:** the full converted/fee/net result, the minimum fee, zero, an amount exactly equal to its fee (net 0), an amount below the fee (throws), and error propagation.

My first draft had wrong expected values for JPY and KWD, because I forgot that their minor units differ from the euro's. I corrected them, so the suite now matches what the current code actually does.

I didn't test amounts near `MAX_SAFE_INTEGER` that convert into a result outside the safe range. The code doesn't check the result, so I couldn't write a meaningful expectation. You may want to decide how that case should behave while you change the module.

I haven't committed anything.