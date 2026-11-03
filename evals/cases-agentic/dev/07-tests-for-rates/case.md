# Tests for the untested rates module (TypeScript)

Tests the quality of tests an agent writes for existing, untested code that is about to change: `src/rates.ts` holds currency conversion with per-currency minor units, tie-breaking rounding modes (half-up and half-even), a percentage fee with a minimum and a cap, and error cases for unknown currencies, fractional amounts and fees that exceed the amount. The agent must add a suite in the project's test location that passes on the unchanged code, without touching the source. The central check is mutation-based: ten hidden single-change mutants of `rates.ts` (a cap off by one, a fee one below the minimum, a zero amount charged, the wrong rounding mode, truncated negatives, a wrong minor-unit count, a swapped currency, a missing error case, a missing cover-the-fee error, rounding by the wrong currency) are laid over a copy of the project, and the agent's tests must fail on at least eight. Tests that only cover the happy path, skip boundaries, ties and error cases, or restate the implementation cannot pass that check.

## Prompt

`src/rates.ts` is the one module here without tests, and we're about to change it. Can you add a proper test suite for it first? Please leave the code itself alone.
