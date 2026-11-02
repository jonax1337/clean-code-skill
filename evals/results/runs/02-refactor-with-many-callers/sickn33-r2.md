```ts
const BOOK_CATEGORY = "books";
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;

const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;

interface PricedProduct {
  price: number;
  category?: string;
}

export function getPrice(product: PricedProduct, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember
    ? product.price * memberMultiplierFor(product)
    : product.price;

  const finalPrice = coupon === SAVE10_COUPON
    ? applySave10(memberPrice)
    : memberPrice;

  return roundToCents(finalPrice);
}

function memberMultiplierFor(product: PricedProduct): number {
  return product.category === BOOK_CATEGORY
    ? BOOK_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
}

function applySave10(price: number): number {
  return Math.max(0, price - SAVE10_DISCOUNT);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- `getPrice` now reads as the pricing steps: member discount, then coupon, then rounding. Each helper does one thing.
- The magic numbers and strings are named constants.
- The nested `if`s became a ternary, and the manual clamp became `Math.max(0, …)`.
- The coupon check collapses to `coupon === "SAVE10"`. The old truthiness guard was redundant, since `undefined` and `""` never equal `"SAVE10"`.
- `p` is now `product`, and the return type is explicit.

**Behavior preserved**
- The multipliers are applied in the same order, and the clamp to 0 still happens only when the coupon is applied. A negative price with no coupon stays negative, as before.
- `NaN` inputs still produce `NaN`.
- The function name, parameter order and export are unchanged, so the 40 call sites need no edits.

**Things to check**
- I replaced `p: any` with `PricedProduct`. I can't see the call sites, so run `tsc` to confirm they type-check. If any pass objects without a numeric `price`, either fix them or temporarily revert the parameter to `any`.
- `==` became `===`. This only differs if `category` is a `String` object rather than a primitive, which is very unlikely.
- Because this is untested money logic, I'd add characterization tests before merging. They should cover books and non-books, member and non-member, `SAVE10` on a price below 10, an unknown coupon, and rounding such as `19.995`.