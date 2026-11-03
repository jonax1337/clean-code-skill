import type { Product } from "../catalog.ts";
import { getPrice } from "../pricing.ts";

export function priceListRows(products: Product[]): string[] {
  return products.map(
    (product) =>
      `${product.sku};${product.title};${getPrice(product, false)};${getPrice(product, true)}`,
  );
}
