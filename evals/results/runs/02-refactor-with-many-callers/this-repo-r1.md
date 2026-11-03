I refactored `getPrice` with the same exported name, parameter order and return value. I could not run anything here, so neither the code nor the tests below have been executed.

```ts
const BOOKS_CATEGORY = "books";
const BOOKS_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_AMOUNT = 10;

export interface PricedProduct {
  price: number;
  category?: string;
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

function memberMultiplier(category: string | undefined): number {
  return category === BOOKS_CATEGORY ? BOOKS_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

Characterization tests (assumes a Jest/Vitest-style `describe/it/expect`; adjust the import and path to your setup):

```ts
import { getPrice } from "./pricing";

describe("getPrice", () => {
  it("leaves the price alone for non-members without a coupon", () => {
    expect(getPrice({ price: 20, category: "toys" }, false)).toBe(20);
  });

  it("gives members 10% off books", () => {
    expect(getPrice({ price: 10, category: "books" }, true)).toBe(9);
  });

  it("gives members 5% off other categories, rounded to cents", () => {
    expect(getPrice({ price: 19.99, category: "toys" }, true)).toBe(18.99);
  });

  it("applies the member discount before SAVE10", () => {
    expect(getPrice({ price: 100, category: "books" }, true, "SAVE10")).toBe(80);
  });

  it("never lets SAVE10 push the price below zero", () => {
    expect(getPrice({ price: 5, category: "toys" }, false, "SAVE10")).toBe(0);
  });

  it("ignores unknown and empty coupons", () => {
    expect(getPrice({ price: 20, category: "toys" }, false, "BOGUS")).toBe(20);
    expect(getPrice({ price: 20, category: "toys" }, false, "")).toBe(20);
  });

  it("does not clamp a negative price when no coupon is used", () => {
    expect(getPrice({ price: -5, category: "toys" }, false)).toBe(-5);
  });
});
```

What changed:
- **Structure:** the nested `if`/`else` is now a member-discount step, a coupon step and a rounding step. The member multiplier and rounding each have a small named helper.
- **Constants:** the magic numbers and strings (`0.9`, `0.95`, `"books"`, `"SAVE10"`, `10`) now have names.
- **Coupon check:** `if (coupon) { if (coupon == "SAVE10") … }` became `coupon === SAVE10_COUPON`, which is equivalent for `string | undefined`.
- **Clamp:** `if (price < 0) price = 0` became `Math.max(0, …)`, which gives the same result. The clamp still applies only when the coupon is used, as the last test pins down.
- **Types:** `p: any` is now `PricedProduct`, and the return type is explicitly `number`.

Things to check:
- **Type check:** the new parameter type is the one change that could affect the ~40 callers. A caller that passes `any` or an object with extra fields will compile, but one whose `category` is not a `string`, or that passes a fresh object literal with extra properties, will now fail. Run `tsc` before merging. If it flags anything, fix the caller's data rather than loosening the type.
- **Loose equality:** the old `==` on `category` also matched non-string values that coerce to `"books"`, such as `["books"]`. `===` does not. This only matters if a caller passes something other than a string, and the type check should show whether any do.
- **Tests:** I wrote the expected values by hand and did not run them, so run them against the original function first to confirm they pin its current behavior.

I left `isMember` as a boolean parameter because changing it would alter the signature that all the callers use.