Because I can't run anything here, I pinned the current behavior with characterization tests first. Run them against the old code, then swap in the refactor and run them again.

**1. Pin the behavior (`pricing.test.ts`)**

```ts
import { describe, it, expect } from "vitest"; // or jest: same API
import { getPrice } from "./pricing";

describe("getPrice", () => {
  const book = { price: 20, category: "books" };
  const toy = { price: 20, category: "toys" };

  it("charges full price to non-members", () => {
    expect(getPrice(book, false)).toBe(20);
    expect(getPrice(toy, false)).toBe(20);
  });
  it("gives members 10% off books", () => {
    expect(getPrice(book, true)).toBe(18);
  });
  it("gives members 5% off everything else", () => {
    expect(getPrice(toy, true)).toBe(19);
    expect(getPrice({ price: 20 }, true)).toBe(19);
  });
  it("applies SAVE10 after the member discount", () => {
    expect(getPrice(book, true, "SAVE10")).toBe(8);
  });
  it("never drops below zero with SAVE10", () => {
    expect(getPrice({ price: 5, category: "toys" }, false, "SAVE10")).toBe(0);
  });
  it("ignores unknown or empty coupons", () => {
    expect(getPrice(toy, false, "BOGUS")).toBe(20);
    expect(getPrice(toy, false, "")).toBe(20);
    expect(getPrice(toy, false, "save10")).toBe(20);
  });
  it("rounds to cents", () => {
    expect(getPrice({ price: 9.99, category: "toys" }, true)).toBe(9.49);
  });
});
```

**2. Refactor (`pricing.ts`)**

```ts
const BOOK_MEMBER_RATE = 0.9;
const DEFAULT_MEMBER_RATE = 0.95;
const SAVE10_AMOUNT = 10;

function memberRate(category: string): number {
  return category === "books" ? BOOK_MEMBER_RATE : DEFAULT_MEMBER_RATE;
}

function applyCoupon(price: number, coupon?: string): number {
  return coupon === "SAVE10" ? Math.max(0, price - SAVE10_AMOUNT) : price;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  const discounted = isMember ? p.price * memberRate(p.category) : p.price;
  return roundToCents(applyCoupon(discounted, coupon));
}
```

**What changed and why**
- The signature and export are unchanged, so the ~40 call sites are untouched.
- The duplicated `isMember` branches became one decision, the member rate, in `memberRate`.
- `if (coupon) { if (coupon == "SAVE10") … }` collapsed to a single check, because `"SAVE10"` is already truthy.
- `if (price < 0) price = 0` became `Math.max(0, …)`. They behave the same, including for `NaN`, which passes through unchanged in both versions.
- The magic numbers are now named constants, and rounding has its own function.

**Equivalence notes**
- `==` became `===`. This only differs if `category` were a `String` wrapper object, which is not realistic, but it is the one theoretical difference.
- I left `p: any` alone. Tightening it (e.g. `{ price: number; category?: string }`) could break some of the 40 callers, so it should be a separate step once the compiler can show you which ones.

**Log**
1. Wrote characterization tests to pin the current behavior, so the refactor can be proven safe.
2. Collapsed the duplicated member-discount branches into `memberRate`, to keep one decision in one place.
3. Extracted `applyCoupon` and `roundToCents` and named the constants, to make each step readable.
4. Kept the public signature unchanged, so the 40 callers are unaffected.
5. Did not run the tests, crapper, dryer, or mutator, and made no commits, because this session has no tools. Please run the tests against the old code and then the new code. The new functions are all tiny, so CRAP scores should be well under 10.