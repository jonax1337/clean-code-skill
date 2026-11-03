Here is the refactor. I couldn't run anything in this session, so none of it has been type-checked or tested.

```ts
// pricing.ts
export interface PricedProduct {
  price: number;
  category: string;
}

const BOOK_CATEGORY = "books";
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;

const SAVE10_COUPON = "SAVE10";
const SAVE10_AMOUNT = 10;

function memberMultiplier(category: string): number {
  return category === BOOK_CATEGORY ? BOOK_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(product: PricedProduct, isMember: boolean, coupon?: string): number {
  let price = product.price;

  if (isMember) {
    price *= memberMultiplier(product.category);
  }
  if (coupon === SAVE10_COUPON) {
    price = Math.max(0, price - SAVE10_AMOUNT);
  }

  return roundToCents(price);
}
```

Characterization tests, with the inputs inline. Adjust the import line to your runner (Jest/Vitest):

```ts
// pricing.test.ts
import { describe, it, expect } from "vitest";
import { getPrice } from "./pricing";

const book = { price: 100, category: "books" };
const toy = { price: 100, category: "toys" };

describe("getPrice", () => {
  it("charges full price to non-members", () => {
    expect(getPrice(book, false)).toBe(100);
  });
  it("gives members 10% off books", () => {
    expect(getPrice(book, true)).toBe(90);
  });
  it("gives members 5% off other categories", () => {
    expect(getPrice(toy, true)).toBe(95);
  });
  it("applies SAVE10 after the member discount", () => {
    expect(getPrice(book, true, "SAVE10")).toBe(80);
  });
  it("never lets SAVE10 push the price below zero", () => {
    expect(getPrice({ price: 5, category: "toys" }, false, "SAVE10")).toBe(0);
  });
  it("ignores unknown and empty coupons", () => {
    expect(getPrice(toy, false, "OTHER")).toBe(100);
    expect(getPrice(toy, false, "")).toBe(100);
  });
  it("rounds to cents", () => {
    expect(getPrice({ price: 19.99, category: "toys" }, true)).toBe(18.99);
  });
});
```

**What changed**
- The nested `if`s are now a member multiplier chosen by category, then the coupon, then rounding. The order of operations is the same: discount, then `-10` clamped at 0, then round.
- Named constants replace the magic numbers and strings. `memberMultiplier` and `roundToCents` are small helpers whose names say what they do.
- `==` became `===`. For string comparison this behaves the same.
- `any` became `PricedProduct`, and `p` became `product`. The parameter order is unchanged, so the call sites don't need edits.

**What I left alone**
- `isMember: boolean` is a flag argument. Changing it would alter the signature across your ~40 callers, so I kept it.

**Please check**
- **Type check:** run `tsc` before merging. The `any` was hiding whatever callers pass in. If some callers pass objects with a different shape, such as `price` as a string or a missing `category`, the compiler will flag them. Fix the type at those call sites rather than reverting to `any`. At runtime, behavior is identical for well-formed inputs.
- **Tests:** run the new tests against the original function first, then against the refactor. I derived the expected values by hand and haven't run them.