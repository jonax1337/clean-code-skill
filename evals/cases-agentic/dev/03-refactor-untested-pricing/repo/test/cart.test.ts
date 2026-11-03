import assert from "node:assert/strict";
import { test } from "node:test";

import { cartTotal } from "../src/cart.ts";
import type { Product } from "../src/catalog.ts";

const book: Product = { sku: "B1", title: "Refactoring", price: 40, category: "books", stock: 3 };
const game: Product = { sku: "G1", title: "Go", price: 20, category: "games", stock: 1 };

test("members get the member price on every line", () => {
  const total = cartTotal({ lines: [{ product: book, quantity: 1 }, { product: game, quantity: 2 }] }, true);
  assert.equal(total, 74);
});

test("a cart coupon applies once to the whole cart", () => {
  const total = cartTotal({ lines: [{ product: game, quantity: 1 }], coupon: "SAVE10" }, false);
  assert.equal(total, 10);
});
