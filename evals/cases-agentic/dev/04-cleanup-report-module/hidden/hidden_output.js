import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildReport, formatMoney } from '../src/report.js';
import * as original from './oracle.js';

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

function seededRandom(seed) {
  let state = seed;
  return () => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
}

const sameReport = (sales, options) =>
  assert.equal(buildReport(sales, options), original.buildReport(sales, options));

const everyRegion = (make) => ['DE', 'FR', 'UK'].map(make);

test('a report with all three regions is laid out as before', () => {
  const sales = [
    sale('DE', 'Widget Pro', 12, 49.9, { date: '2024-03-04' }),
    sale('FR', 'Gadget Mini', 100, 12.5, { discountPct: 10, date: '2024-03-05' }),
    sale('UK', 'Support Contract Premium Plus', 1, 9800, { date: '2024-03-06' }),
    sale('DE', 'Pallet', 2000, 7.77, { date: '2024-03-01' }),
  ];
  assert.equal(
    buildReport(sales),
    [
      'SALES REPORT',
      '',
      '== Germany ==',
      'Pallet                2000    17.567,97 € *',
      'Widget Pro              12       712,57 €',
      'Subtotal DE: 18.280,54 €',
      '',
      '== France ==',
      'Gadget Mini            100     1 282,50 €',
      'Subtotal FR: 1 282,50 €',
      '',
      '== United Kingdom ==',
      'Support Contract Pr…     1     £11,760.00 *',
      'Subtotal UK: £11,760.00',
      '',
      'Rows: 4',
      'Large orders: 2',
      '',
    ].join('\n'),
  );
});

test('product names of exactly 20 characters stay, longer ones are cut to 19 plus an ellipsis', () => {
  const sales = [
    sale('DE', '12345678901234567890', 1, 1),
    sale('FR', '123456789012345678901', 1, 1),
    sale('UK', '1234567890123456789', 1, 1),
  ];
  const report = buildReport(sales);
  assert.match(report, /^12345678901234567890 {2}/m);
  assert.match(report, /^1234567890123456789… {2}/m);
  assert.match(report, /^1234567890123456789 {3}/m);
  sameReport(sales);
});

test('amounts around the thousands separators and the large order mark', () => {
  const prices = [0, 0.01, 0.5, 8.33, 83.33, 833.33, 8333.33, 83333.33, 833333.33, 8333333.33];
  sameReport(prices.flatMap((price) => everyRegion((region) => sale(region, 'Item', 1, price))));
  const edges = [8333.32, 8333.325, 8333.33, 9999.99, 10000];
  const sales = edges.flatMap((price) => everyRegion((region) => sale(region, 'Edge', 1, price)));
  sameReport(sales);
  assert.match(buildReport(sales), / \*$/m);
});

test('bulk discount starts at 100 units and combines with the percentage discount', () => {
  const sales = [99, 100, 101].flatMap((units) =>
    [0, 10].flatMap((discountPct) =>
      everyRegion((region) => sale(region, 'Bulk', units, 3.33, { discountPct })),
    ),
  );
  sameReport(sales);
});

test('VAT and discounts are computed in the old order, so cents match', () => {
  const sales = [
    sale('DE', 'case-a', 44, 84.66, { discountPct: 15 }),
    sale('UK', 'case-b', 4, 3.31, { discountPct: 12.5 }),
    sale('FR', 'case-c', 31, 142.7, { discountPct: 15 }),
    sale('DE', 'case-d', 150, 132.74, { discountPct: 10 }),
    sale('FR', 'case-e', 148, 3.5, { discountPct: 5 }),
    sale('DE', 'case-f', 79, 47.5),
    sale('FR', 'case-g', 140, 128.58, { discountPct: 12.5 }),
  ];
  sameReport(sales);
  const report = buildReport(sales);
  assert.match(report, /^case-a +44 +3\.767,87 €$/m);
  assert.match(report, /^case-b +4 +£13\.91$/m);
  assert.match(report, /^case-c +31 +4 512,18 €$/m);
});

test('sales without units, with negative units or from other regions are left out', () => {
  const sales = [
    sale('DE', 'Zero', 0, 5),
    sale('FR', 'Negative', -3, 5),
    sale('US', 'Overseas', 4, 5),
    sale('UK', 'Kept', 1, 5),
  ];
  assert.equal(
    buildReport(sales),
    [
      'SALES REPORT',
      '',
      '== United Kingdom ==',
      'Kept                     1          £6.00',
      'Subtotal UK: £6.00',
      '',
      'Rows: 1',
      'Large orders: 0',
      '',
    ].join('\n'),
  );
  assert.equal(buildReport([sale('US', 'Overseas', 4, 5)]), 'SALES REPORT\n\nNo sales.\n');
});

test('the month filter and the ordering by date', () => {
  const sales = [
    sale('DE', 'B-late', 1, 10, { date: '2024-03-20' }),
    sale('DE', 'A-tie-first', 1, 10, { date: '2024-03-05' }),
    sale('DE', 'A-tie-second', 2, 10, { date: '2024-03-05' }),
    sale('DE', 'April', 1, 10, { date: '2024-04-01' }),
    sale('DE', 'Feb', 1, 10, { date: '2024-02-29' }),
  ];
  sameReport(sales, { month: '2024-03' });
  sameReport(sales, { month: '2024-05' });
  sameReport(sales, {});
  sameReport(sales, undefined);
  assert.match(buildReport(sales, { month: '2024-03' }), /^SALES REPORT 2024-03\n/);
  const report = buildReport(sales);
  assert.ok(report.indexOf('Feb') < report.indexOf('A-tie-first'));
  assert.ok(report.indexOf('A-tie-first') < report.indexOf('A-tie-second'));
});

test('the input list is not reordered or modified', () => {
  const sales = [
    sale('DE', 'Late', 1, 10, { date: '2024-03-20' }),
    sale('DE', 'Early', 1, 10, { date: '2024-03-01' }),
  ];
  const snapshot = structuredClone(sales);
  buildReport(sales);
  buildReport(sales, { month: '2024-03' });
  assert.deepEqual(sales, snapshot);
});

test('unsupported formats and malformed months are rejected as before', () => {
  assert.throws(() => buildReport([], { format: 'legacy' }), { message: 'unsupported format: legacy' });
  assert.throws(() => buildReport([], { format: 'csv' }), { message: 'unsupported format: csv' });
  assert.equal(buildReport([], { format: 'text' }), 'SALES REPORT\n\nNo sales.\n');
  assert.throws(() => buildReport([], { month: '2024-3' }), { message: 'bad month: 2024-3' });
  assert.throws(() => buildReport([], { month: 'March' }), { message: 'bad month: March' });
});

test('formatMoney pins the regional formats, rounding, negatives and unknown regions', () => {
  assert.equal(formatMoney(0, 'DE'), '0,00 €');
  assert.equal(formatMoney(999.99, 'DE'), '999,99 €');
  assert.equal(formatMoney(1000, 'DE'), '1.000,00 €');
  assert.equal(formatMoney(1234567.891, 'DE'), '1.234.567,89 €');
  assert.equal(formatMoney(1234567.891, 'FR'), '1 234 567,89 €');
  assert.equal(formatMoney(1234567.891, 'UK'), '£1,234,567.89');
  assert.equal(formatMoney(-1234.5, 'DE'), '-1.234,50 €');
  assert.equal(formatMoney(-1234.5, 'UK'), '-£1,234.50');
  assert.equal(formatMoney(1.005, 'DE'), '1,00 €');
  assert.equal(formatMoney(1.115, 'UK'), '£1.11');
  assert.throws(() => formatMoney(1, 'US'), { message: 'unknown region: US' });
  assert.throws(() => formatMoney(1), { message: 'unknown region: undefined' });
});

test('random reports match the original implementation exactly', () => {
  const random = seededRandom(20240311);
  const pick = (items) => items[Math.floor(random() * items.length)];
  const regions = ['DE', 'FR', 'UK', 'DE', 'FR', 'UK', 'US'];
  const dates = ['2024-02-27', '2024-03-01', '2024-03-01', '2024-03-15', '2024-03-31', '2024-04-02'];
  const unitCounts = [-1, 0, 1, 2, 7, 50, 99, 100, 101, 400, 3000];
  const basePrices = [0, 0.01, 1.99, 12.5, 49.9, 133.33, 1999.99, 25000];
  for (let round = 0; round < 400; round++) {
    const sales = Array.from({ length: Math.floor(random() * 14) }, () => {
      const cents = random() < 0.5 ? 0 : Math.round(random() * 9999) / 100;
      return sale(
        pick(regions),
        'x'.repeat(1 + Math.floor(random() * 30)),
        pick(unitCounts),
        pick(basePrices) + cents,
        { discountPct: pick([0, 0, 5, 10, 12.5, 15, 33]), date: pick(dates) },
      );
    });
    sameReport(sales, pick([undefined, {}, { month: '2024-03' }, { month: '2024-04' }, { month: '2023-12' }]));
  }
});

test('random amounts format like the original', () => {
  const random = seededRandom(7);
  for (let round = 0; round < 600; round++) {
    const sign = random() < 0.2 ? -1 : 1;
    const amount = (sign * Math.round(random() * 1e9)) / (random() < 0.5 ? 100 : 1000);
    for (const region of ['DE', 'FR', 'UK']) {
      assert.equal(formatMoney(amount, region), original.formatMoney(amount, region));
    }
  }
});
