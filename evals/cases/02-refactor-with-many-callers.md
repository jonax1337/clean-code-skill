# Refactor a function with many callers (TypeScript)

Tests: behavior preservation, magic numbers (G25), keeping a public signature stable, no over-engineering.

## Prompt

Please refactor this to be clean. It's exported from `pricing.ts` and called from about 40 places across the codebase. Behavior must not change.

```ts
export function getPrice(p: any, isMember: boolean, coupon?: string) {
  let price = p.price;
  if (p.category == "books") {
    if (isMember) {
      price = price * 0.9;
    }
  } else {
    if (isMember) {
      price = price * 0.95;
    }
  }
  if (coupon) {
    if (coupon == "SAVE10") {
      price = price - 10;
      if (price < 0) price = 0;
    }
  }
  return Math.round(price * 100) / 100;
}
```

## Assertions

1. Behavior is preserved for all inputs: member discount (10 % books, 5 % otherwise) is applied before the coupon, `SAVE10` subtracts 10 and floors at 0, unknown coupons do nothing, and the result is rounded to 2 decimals the same way.
2. The discount rates and coupon amount are named (constants or a lookup table) instead of bare literals.
3. The exported signature stays call-compatible with the ~40 existing callers, or the response explicitly flags the breaking change and gives a migration path. Silently changing the signature fails.
4. `any` is replaced by a type for the product parameter, or the response explicitly mentions it.
5. No over-engineering: no class hierarchy, strategy pattern or plugin mechanism for two discount rates and one coupon.
