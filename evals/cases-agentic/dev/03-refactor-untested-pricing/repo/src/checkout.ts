import { getPrice } from "./pricing.ts";

export interface OrderLine {
  sku: string;
  unitPrice: number;
  category?: string;
  quantity: number;
}

export function lineTotals(lines: OrderLine[], isMember: boolean): number[] {
  return lines.map(
    (line) => getPrice({ price: line.unitPrice, category: line.category }, isMember) * line.quantity,
  );
}
