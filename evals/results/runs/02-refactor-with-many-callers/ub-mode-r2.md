I couldn't run anything here, so the tests below are written but not run. Please run them against the **old** implementation first to confirm they pass, then swap in the new one.

## Log
1. **Pinned current behavior** with characterization tests, written before touching the code.
2. **Refactored** with the same exported name and signature, so the ~40 call sites are untouched.
3. **Left `p: any` alone.** Tightening it could break callers at compile time, which goes beyond "behavior must not change".

## 1. Characterization tests (`pricing.test.ts`)

```ts
import { getPrice } from "./pricing";

describe("getPrice", () => {
  const book = { price: 20, category: "books" };
  const toy = { price: 20, category: "toys" };

  it("charges list price to non-members", () => {
    expect(getPrice(book, false)).toBe(20);
    expect(getPrice(toy, false)).toBe(20);
  });

  it("gives members 10% off books and 5% off everything else", () => {
    expect(getPrice(book, true)).toBe(18);
    expect(getPrice(toy, true)).toBe(19);
  });

  it("applies SAVE10 after the member discount", () => {
    expect(getPrice(book, true, "SAVE10")).toBe(8);
    expect(getPrice(toy, false, "SAVE10")).toBe(10);
  });

  it("never lets SAVE10 push the price below zero", () => {
    expect(getPrice({ price: 5, category: "toys" }, false, "SAVE10")).toBe(0);
  });

  it("ignores unknown or empty coupons", () => {
    expect(getPrice(toy, false, "NOPE")).toBe(20);
    expect(getPrice(toy, false, "")).toBe(20);
  });

  it("rounds to two decimals", () => {
    expect(getPrice({ price: 9.99, category: "books" }, true)).toBe(8.99);
    expect(getPrice({ price: 1.005, category: "toys" }, false)).toBe(1);
  });

  it("does not clamp a negative price when no coupon is applied", () => {
    expect(getPrice({ price: -5, category: "toys" }, false)).toBe(-5);
  });
});
```

## 2. Refactor (`pricing.ts`)

```ts
const BOOKS_MEMBER_RATE = 0.9;
const DEFAULT_MEMBER_RATE = 0.95;
const NON_MEMBER_RATE = 1;
const SAVE10_AMOUNT = 10;

function memberRate(category: unknown, isMember: boolean): number {
  if (!isMember) return NON_MEMBER_RATE;
  return category == "books" ? BOOKS_MEMBER_RATE : DEFAULT_MEMBER_RATE;
}

function applyCoupon(price: number, coupon?: string): number {
  return coupon === "SAVE10" ? Math.max(0, price - SAVE10_AMOUNT) : price;
}

const roundToCents = (n: number) => Math.round(n * 100) / 100;

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  const discounted = p.price * memberRate(p.category, isMember);
  return roundToCents(applyCoupon(discounted, coupon));
}
```

## Why it's the same
- **Rates and order of operations:** the member multiplier comes first, then the coupon, then rounding, with the same floating-point steps as before.
- **Non-members:** they now multiply by `1`, which gives the same number. A string `price` is coerced the same way it was before.
- **Coupon clamp:** `Math.max(0, x)` matches `if (x < 0) x = 0`, including for `NaN`.
- **Category check:** I kept the loose `==` on purpose, so `category` behaves exactly as before.
- **Each rule has one home:** the rates, coupon amount and rounding are now named in one place each.

## Not done (needs your decision)
- **Tooling and commits:** the crapper, dryer and mutator tools aren't available here, and this isn't a git repo, so I made no commits. Each step above would be its own small commit: tests, then refactor.
- **Typing `p`:** a follow-up could replace `any` with `{ price: number; category?: string }`, but that may surface compile errors at some of the 40 callers.