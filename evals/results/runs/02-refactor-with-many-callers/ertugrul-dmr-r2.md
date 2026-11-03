```ts
interface PricedProduct {
  price: number;
  category?: string;
}

const BOOKS_CATEGORY = "books";
const BOOKS_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;

function memberMultiplierFor(product: PricedProduct): number {
  return product.category === BOOKS_CATEGORY
    ? BOOKS_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
}

function applyCoupon(price: number, coupon?: string): number {
  if (coupon !== SAVE10_COUPON) {
    return price;
  }
  return Math.max(0, price - SAVE10_DISCOUNT);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}

export function getPrice(
  product: PricedProduct,
  isMember: boolean,
  coupon?: string,
): number {
  const memberPrice = isMember
    ? product.price * memberMultiplierFor(product)
    : product.price;

  return roundToCents(applyCoupon(memberPrice, coupon));
}
```

**Fixed**
- G25: Extracted the magic numbers and strings (`0.9`, `0.95`, `10`, `"books"`, `"SAVE10"`) into named constants.
- G30/G34: Split the function into member multiplier, coupon, and rounding steps, so `getPrice` now reads as a short pipeline.
- G5/G28: Removed the duplicated `if (isMember)` branches. The category check is now in `memberMultiplierFor`.
- G16: Replaced the manual `if (price < 0) price = 0` clamp with `Math.max(0, …)`. Merged the nested `if (coupon) { if (coupon == …) }` into one guard clause.
- TS3/N1: Replaced `p: any` with a `PricedProduct` interface, added an explicit `number` return type, and gave `p` a descriptive name.
- TS2 (partial): `"books"` and `"SAVE10"` are now constants. I did not turn them into enums or union types because that would change the public signature.
- G24: Replaced `==` with `===`. For string comparison this behaves identically.

**Behavior preserved**
- The multiplications, the order of operations (member discount, then coupon, then rounding), and the `NaN` and negative-price edge cases are unchanged. I kept `price * 0.9` instead of `1 - 0.1`, because a different float computation could change results at the cent boundary.

**Deliberately not changed**
- F3: `isMember` is a flag argument. Splitting it into `getMemberPrice` and `getRegularPrice` would be cleaner, but it would touch all ~40 call sites. If you want that, I'd add the new functions and migrate callers gradually.
- Typing `p`: if any caller passes something that doesn't satisfy `PricedProduct`, for example a `price` stored as a string, `tsc` will flag it. That's useful, but it is a compile-time change. If you want zero risk, temporarily use `product: PricedProduct | any`, though that defeats TS3.

Since I can't run the code or tests here, run `npm run build` and `npm test` to confirm. A quick table test for these cases would back up the "no behavior change" claim:
- book and non-book prices, with and without membership
- `SAVE10` on prices below 10 (clamps to 0)
- an unknown coupon
- an empty-string coupon