import { InvalidAmountError, UnknownCurrencyError } from "./errors.ts";

export type RoundingMode = "half-up" | "half-even";

export interface Quote {
  converted: number;
  fee: number;
  net: number;
}

interface CurrencyRule {
  /** Decimal places of the minor unit: 2 for cents, 0 for yen, 3 for fils. */
  minorUnits: number;
  /** Settles ties when an amount does not divide evenly. Half-up rounds away from zero. */
  rounding: RoundingMode;
  /** Units of this currency per euro, in millionths. */
  perEuroMicros: number;
  /** Smallest fee charged on a non-zero amount, in minor units. */
  minFee: number;
  /** Largest fee charged, in minor units. */
  maxFee: number;
}

const FEE_BASIS_POINTS = 250n;
const BASIS_POINTS_PER_UNIT = 10_000n;

const RULES = new Map<string, CurrencyRule>([
  ["EUR", { minorUnits: 2, rounding: "half-even", perEuroMicros: 1_000_000, minFee: 30, maxFee: 5000 }],
  ["USD", { minorUnits: 2, rounding: "half-up", perEuroMicros: 1_100_000, minFee: 30, maxFee: 5000 }],
  ["CHF", { minorUnits: 2, rounding: "half-even", perEuroMicros: 950_000, minFee: 30, maxFee: 5000 }],
  ["JPY", { minorUnits: 0, rounding: "half-up", perEuroMicros: 162_500_000, minFee: 50, maxFee: 8000 }],
  ["KWD", { minorUnits: 3, rounding: "half-even", perEuroMicros: 325_000, minFee: 300, maxFee: 1500 }],
]);

export function minorUnitsOf(currency: string): number {
  return ruleFor(currency).minorUnits;
}

/** Converts an amount between two supported currencies via the euro rate, rounding in the target currency. */
export function convert(amountMinor: number, from: string, to: string): number {
  assertWholeAmount(amountMinor);
  const source = ruleFor(from);
  const target = ruleFor(to);
  const numerator = BigInt(amountMinor) * 10n ** BigInt(target.minorUnits) * BigInt(target.perEuroMicros);
  const denominator = 10n ** BigInt(source.minorUnits) * BigInt(source.perEuroMicros);
  return divideRounded(numerator, denominator, target.rounding);
}

/** The fee for moving an amount in the given currency: 2.5%, within the currency's minimum and maximum. */
export function feeFor(amountMinor: number, currency: string): number {
  assertWholeAmount(amountMinor);
  const rule = ruleFor(currency);
  if (amountMinor < 0) {
    throw new InvalidAmountError(`No fee can be charged on a negative amount: ${amountMinor}`);
  }
  if (amountMinor === 0) {
    return 0;
  }
  const percentage = divideRounded(BigInt(amountMinor) * FEE_BASIS_POINTS, BASIS_POINTS_PER_UNIT, rule.rounding);
  return Math.min(Math.max(percentage, rule.minFee), rule.maxFee);
}

/** Converts an amount and charges the fee in the target currency; the amount has to cover the fee. */
export function quote(amountMinor: number, from: string, to: string): Quote {
  const converted = convert(amountMinor, from, to);
  const fee = feeFor(converted, to);
  if (fee > converted) {
    throw new InvalidAmountError(`${converted} ${to} does not cover the fee of ${fee}`);
  }
  return { converted, fee, net: converted - fee };
}

function ruleFor(currency: string): CurrencyRule {
  const rule = RULES.get(currency);
  if (rule === undefined) {
    throw new UnknownCurrencyError(currency);
  }
  return rule;
}

function assertWholeAmount(amountMinor: number): void {
  if (!Number.isSafeInteger(amountMinor)) {
    throw new InvalidAmountError(`Amount must be a whole number of minor units, got ${amountMinor}`);
  }
}

/** numerator / denominator rounded to a whole number; ties go away from zero or to the even neighbor. */
function divideRounded(numerator: bigint, denominator: bigint, mode: RoundingMode): number {
  const negative = numerator < 0n;
  const magnitude = negative ? -numerator : numerator;
  let quotient = magnitude / denominator;
  const doubledRemainder = (magnitude % denominator) * 2n;
  const isTie = doubledRemainder === denominator;
  if (doubledRemainder > denominator || (isTie && (mode === "half-up" || quotient % 2n === 1n))) {
    quotient += 1n;
  }
  return Number(negative ? -quotient : quotient);
}
