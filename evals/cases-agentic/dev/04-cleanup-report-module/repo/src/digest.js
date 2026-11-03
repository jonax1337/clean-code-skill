import { formatMoney } from './report.js';

export function topDeals(sales, count = 3) {
  return sales
    .filter((sale) => sale.units > 0)
    .map((sale) => ({ sale, amount: sale.units * sale.unitPrice }))
    .sort((a, b) => b.amount - a.amount)
    .slice(0, count)
    .map(({ sale, amount }) => `${sale.rep}: ${formatMoney(amount, sale.region)}`);
}
