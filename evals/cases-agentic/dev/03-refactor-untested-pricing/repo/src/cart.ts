import type { Product } from "./catalog.ts";
import { getPrice } from "./pricing.ts";

export interface CartLine {
  product: Product;
  quantity: number;
}

export interface Cart {
  lines: CartLine[];
  coupon?: string;
}

export function cartTotal(cart: Cart, isMember: boolean): number {
  let total = 0;
  for (const line of cart.lines) {
    total += getPrice(line.product, isMember) * line.quantity;
  }
  if (cart.coupon) {
    total = getPrice({ price: total, category: "mixed" }, false, cart.coupon);
  }
  return Math.round(total * 100) / 100;
}
