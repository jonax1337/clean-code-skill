```ts
export interface PricedProduct {
  price: number;
  category?: string;
}

const BOOKS_CATEGORY = "books";
const BOOKS_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;
const CENTS_PER_UNIT = 100;

function memberMultiplierFor(product: PricedProduct): number {
  return product.category === BOOKS_CATEGORY
    ? BOOKS_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
}

function applyMemberDiscount(price: number, product: PricedProduct, isMember: boolean): number {
  return isMember ? price * memberMultiplierFor(product) : price;
}

function applyCoupon(price: number, coupon?: string): number {
  return coupon === SAVE10_COUPON ? Math.max(0, price - SAVE10_DISCOUNT) : price;
}

function roundToCents(price: number): number {
  return Math.round(price * CENTS_PER_UNIT) / CENTS_PER_UNIT;
}

export function getPrice(product: PricedProduct, isMember: boolean, coupon?: string): number {
  const memberPrice = applyMemberDiscount(product.price, product, isMember);
  const couponPrice = applyCoupon(memberPrice, coupon);
  return roundToCents(couponPrice);
}
```

**What changed**
- Fixed: magic numbers and strings extracted to named constants (G25, TS2).
- Fixed: nested `if`s replaced with small single-purpose functions, so `getPrice` reads as three steps: member discount, coupon, rounding (G30, G34).
- Fixed: `any` replaced with a `PricedProduct` interface and an explicit `number` return type (TS3).
- Fixed: `==` became `===`, and the manual `if (price < 0) price = 0` became `Math.max(0, …)`. Both give the same results, including for `NaN`.
- Fixed: renamed `p` to `product` (N1), and only `getPrice` and the type are exported (G8).

**Left alone on purpose**
- **Signature:** `getPrice(product, isMember, coupon?)` keeps its shape, so the ~40 call sites still work. `isMember` is technically a flag argument (F3). Splitting it into something like `getMemberPrice` would be cleaner, but it would change the public API. That is best done as a separate, deliberate migration.

**One compile-time risk**
- Replacing `any` with `PricedProduct` is safe at runtime but could raise type errors at call sites. That happens if a caller passes an object literal with extra properties, or a product whose `price` isn't typed as `number`. Run `tsc` after applying it. If it complains, widen the type, for example `PricedProduct & Record<string, unknown>`, or fix the callers. I couldn't check the call sites from here.