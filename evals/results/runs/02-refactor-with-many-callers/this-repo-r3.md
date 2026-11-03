Here's the refactor. I couldn't run anything in this session, so none of it has been type-checked or tested.

```ts
const BOOKS_CATEGORY = "books";
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;

interface PricedProduct {
  price: number;
  category?: string;
}

export function getPrice(product: PricedProduct, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? product.price * memberMultiplier(product) : product.price;
  const finalPrice = coupon === SAVE10_COUPON ? applySave10(memberPrice) : memberPrice;
  return roundToCents(finalPrice);
}

function memberMultiplier(product: PricedProduct): number {
  return product.category === BOOKS_CATEGORY ? BOOK_MEMBER_MULTIPLIER : DEFAULT_MEMBER_MULTIPLIER;
}

function applySave10(price: number): number {
  return Math.max(0, price - SAVE10_DISCOUNT);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- Nested `if`s became a member multiplier, an optional coupon step and rounding, each with a name.
- Magic numbers and strings are now named constants.
- `any` became a small `PricedProduct` type, and `==` became `===`.
- The signature (name, parameter order, return value) is unchanged, so the ~40 callers need no edits.

**Behavior preserved**
- Only the exact coupon `"SAVE10"` has an effect. Other or empty coupons are ignored, as before.
- The coupon is applied after the member discount, and the clamp at 0 applies only with the coupon, so a negative base price is not clamped without one.
- Rounding stays last.

**Risks to check, since I couldn't run anything**
1. **Type tightening:** `any` → `PricedProduct` could produce compile errors at callers that pass something without a numeric `price`, or object literals with extra properties. Run `tsc` across the repo. If a few callers fail, the errors point to real mismatches. Back the type out only if they are unfixable.
2. **`==` → `===`:** this is identical for string categories. It differs only if some caller passes a non-string `category`, which the new type forbids.

**Tests:** I didn't see an existing test for this function, so before merging I'd add characterization tests against the *original* implementation, then rerun them on the refactor. Cover at least:
- member vs non-member, for books and for a non-book category
- `SAVE10` on a price above 10, exactly 10, and below 10 (clamps to 0)
- an unknown coupon and an empty string coupon
- a price that needs rounding (e.g. 19.99 × 0.95)
- a missing category

I didn't write them because I don't know your test framework or file layout. I can add them once you tell me.