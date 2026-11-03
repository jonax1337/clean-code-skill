```ts
interface Priceable {
  price: number;
  category?: string;
}

const MEMBER_DISCOUNT_BOOKS = 0.9;
const MEMBER_DISCOUNT_DEFAULT = 0.95;
const SAVE10_AMOUNT = 10;

function memberMultiplier(category: string | undefined): number {
  return category === "books" ? MEMBER_DISCOUNT_BOOKS : MEMBER_DISCOUNT_DEFAULT;
}

function applyCoupon(price: number, coupon?: string): number {
  switch (coupon) {
    case "SAVE10":
      return Math.max(0, price - SAVE10_AMOUNT);
    default:
      return price;
  }
}

function roundToCents(value: number): number {
  return Math.round(value * 100) / 100;
}

export function getPrice(p: Priceable, isMember: boolean, coupon?: string): number {
  const memberPrice = isMember ? p.price * memberMultiplier(p.category) : p.price;
  return roundToCents(applyCoupon(memberPrice, coupon));
}
```

**What changed**
- The nested `if`s are now small named helpers, and the magic numbers are named constants.
- The coupon logic is a `switch`, so adding new coupon codes is a one-line change.
- `if (price < 0) price = 0` became `Math.max(0, ...)`. The two behave the same for all inputs, including `NaN`.
- The function and its parameters keep the same order and name, and the rounding is the same, so results are unchanged.

**Two things to check with 40 callers**
1. **Typing:** I replaced `p: any` with a `Priceable` interface. If `tsc` complains at some call sites, for example because `price` is a string or the object is loosely typed, either fix those callers or temporarily revert the parameter to `any`. The runtime behavior is the same either way.
2. **`==` vs `===`:** The original used `p.category == "books"`. The two only differ if `category` is a non-string that coerces to `"books"`, such as a `String` object, which is very unlikely. If you want to be strictly identical, use `==`.