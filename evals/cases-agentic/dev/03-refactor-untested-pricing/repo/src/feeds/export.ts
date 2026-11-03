import { getPrice } from "../pricing.ts";

interface FeedRow {
  id: string;
  price: number;
}

export function feedPrices(rows: FeedRow[], coupon: string): Record<string, number> {
  const prices: Record<string, number> = {};
  for (const row of rows) {
    prices[row.id] = getPrice(row, false, coupon);
  }
  return prices;
}
