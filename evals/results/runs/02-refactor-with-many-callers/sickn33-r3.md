```ts
const BOOK_CATEGORY = "books";
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;

const TEN_OFF_COUPON = "SAVE10";
const TEN_OFF_AMOUNT = 10;

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  let price = p.price;

  if (isMember) {
    price *= memberMultiplierFor(p.category);
  }
  if (coupon === TEN_OFF_COUPON) {
    price = applyTenOffCoupon(price);
  }

  return roundToCents(price);
}

function memberMultiplierFor(category: string): number {
  return category === BOOK_CATEGORY
    ? BOOK_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
}

function applyTenOffCoupon(price: number): number {
  return Math.max(0, price - TEN_OFF_AMOUNT);
}

function roundToCents(amount: number): number {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- The nested `if`s became a flat flow: member discount, then coupon, then rounding. The member check now appears once instead of in both branches.
- Magic numbers and strings are named constants, and each step is a small helper with a single purpose.
- The `if (price < 0) price = 0` clamp became `Math.max(0, ...)`. It is still applied only for the coupon, so a negative `p.price` without a coupon behaves as before. `NaN` also passes through unchanged.
- I kept the exported name and signature (`getPrice(p: any, isMember, coupon?)`), so all 40 call sites are unaffected.

**Things to be aware of**
- I changed `==` to `===`. For string primitives, which is what `category` and `coupon` should be, the results are identical. It would only differ if a caller passed something like a `String` object or a non-string that coerces, which seems unlikely, but revert it if you want a strict guarantee.
- I left `p: any` alone on purpose. Typing it as `{ price: number; category?: string }` would be a good follow-up, but it could cause compile errors at some of the 40 callers, so it deserves its own change.
- I haven't run anything, so before merging, add a few characterization tests that pin current outputs. Good cases are books vs. non-books, member vs. non-member, `SAVE10` on a price under 10, an unknown coupon, and a rounding case like `19.995`. Run them against the old and new versions to confirm they match.