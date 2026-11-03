import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildReport, formatMoney } from '../src/report.js';

const sale = (region, product, units, unitPrice, extra = {}) => ({
  region,
  rep: 'Rep',
  product,
  units,
  unitPrice,
  discountPct: 0,
  date: '2024-03-10',
  ...extra,
});

test('French sales use spaces as thousands separator and 20 percent VAT', () => {
  const report = buildReport([sale('FR', 'Widget Pro', 30, 51)]);
  assert.match(report, /^== France ==$/m);
  assert.match(report, /^Widget Pro +30 +1 836,00 €$/m);
  assert.match(report, /^Subtotal FR: 1 836,00 €$/m);
});

test('British sales use a pound sign and commas', () => {
  const report = buildReport([sale('UK', 'Gadget Mini', 80, 11.2)]);
  assert.match(report, /^== United Kingdom ==$/m);
  assert.match(report, /^Gadget Mini +80 +£1,075\.20$/m);
  assert.match(report, /^Subtotal UK: £1,075\.20$/m);
});

test('discount and bulk discount are applied before VAT', () => {
  const report = buildReport([sale('DE', 'Gadget Mini', 150, 12.5, { discountPct: 10 })]);
  assert.match(report, /^Gadget Mini +150 +1\.907,72 €$/m);
});

test('long product names are cut to 20 characters with an ellipsis', () => {
  const report = buildReport([sale('UK', 'Premium Support Contract', 1, 9800)]);
  assert.match(report, /^Premium Support Con… +1 +£11,760\.00 \*$/m);
});

test('orders of 10000 or more are marked and counted', () => {
  const report = buildReport([sale('FR', 'Pallet', 2000, 7.77), sale('FR', 'Box', 1, 5)]);
  assert.match(report, /^Pallet +2000 +17 715,60 € \*$/m);
  assert.match(report, /^Large orders: 1$/m);
});

test('sales without units and sales from unknown regions are skipped', () => {
  const report = buildReport([sale('DE', 'Zero', 0, 5), sale('US', 'Overseas', 4, 5)]);
  assert.equal(report, 'SALES REPORT\n\nNo sales.\n');
});

test('a month filter keeps only that month and shows it in the title', () => {
  const sales = [sale('DE', 'March', 1, 10), sale('DE', 'April', 1, 10, { date: '2024-04-02' })];
  const report = buildReport(sales, { month: '2024-04' });
  assert.match(report, /^SALES REPORT 2024-04\n/);
  assert.doesNotMatch(report, /March/);
});

test('the input list is not reordered', () => {
  const sales = [sale('DE', 'Late', 1, 10, { date: '2024-03-20' }), sale('DE', 'Early', 1, 10, { date: '2024-03-01' })];
  buildReport(sales);
  assert.deepEqual(sales.map((entry) => entry.product), ['Late', 'Early']);
});

test('unsupported formats and malformed months are rejected', () => {
  assert.throws(() => buildReport([], { format: 'legacy' }), /unsupported format: legacy/);
  assert.throws(() => buildReport([], { month: '2024-3' }), /bad month: 2024-3/);
});

test('formatMoney handles negative amounts and rejects unknown regions', () => {
  assert.equal(formatMoney(-1234.5, 'UK'), '-£1,234.50');
  assert.throws(() => formatMoney(1, 'US'), /unknown region: US/);
});
