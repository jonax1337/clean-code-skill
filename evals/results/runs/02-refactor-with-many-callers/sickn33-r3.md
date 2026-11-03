```ts
const BOOK_CATEGORY = "books";
const BOOK_MEMBER_MULTIPLIER = 0.9;
const DEFAULT_MEMBER_MULTIPLIER = 0.95;
const SAVE10_COUPON = "SAVE10";
const SAVE10_DISCOUNT = 10;

export function getPrice(p: any, isMember: boolean, coupon?: string) {
  const memberPrice = applyMemberDiscount(p.price, p.category, isMember);
  const finalPrice = applyCoupon(memberPrice, coupon);
  return roundToCents(finalPrice);
}

function applyMemberDiscount(price: number, category: string, isMember: boolean) {
  if (!isMember) return price;
  const multiplier = category === BOOK_CATEGORY
    ? BOOK_MEMBER_MULTIPLIER
    : DEFAULT_MEMBER_MULTIPLIER;
  return price * multiplier;
}

function applyCoupon(price: number, coupon?: string) {
  if (coupon !== SAVE10_COUPON) return price;
  return Math.max(0, price - SAVE10_DISCOUNT);
}

function roundToCents(amount: number) {
  return Math.round(amount * 100) / 100;
}
```

**What changed**
- `getPrice` now reads as three steps: member discount, coupon, rounding. Each helper does one thing.
- The magic numbers and strings are named constants.
- The nested `if`s are replaced by early returns and a ternary.
- The `if (price < 0) price = 0` clamp became `Math.max(0, ...)`.
- The helpers are not exported, so the public surface is unchanged. The name, parameters, and return type stay the same, so the ~40 call sites need no edits.

**Behavior preserved**
- The arithmetic is applied in the same order (`price * multiplier`, then `- 10`, then round), so floating-point results are identical.
- An empty or unknown coupon is still ignored.
- `NaN` still passes through, because `Math.max(0, NaN)` is `NaN` and `NaN < 0` was false.

**Things to check**
- I changed `==` to `===` for the category check. The only input where that differs is a `String` object (`new String("books")`) instead of a primitive. That's very unlikely, but search for it if you want to be certain.
- I kept `p: any` on purpose. Tightening it to something like `{ price: number; category: string }` is a good next step, but it could produce compile errors at call sites I can't see, so I'd do it as a separate change.
- I haven't run anything. Before merging, add characterization tests that pin current outputs: member vs non-member, books vs other, `SAVE10` driving the price below zero, an unknown coupon, and a rounding case like `19.995`. Run them against both the old and new versions.