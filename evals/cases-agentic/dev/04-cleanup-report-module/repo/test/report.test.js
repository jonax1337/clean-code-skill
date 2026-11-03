import assert from 'node:assert/strict';
import { test } from 'node:test';
import { buildReport, formatMoney } from '../src/report.js';

const germanSales = [
  { region: 'DE', rep: 'Anke', product: 'Widget Pro', units: 12, unitPrice: 49.9, discountPct: 0, date: '2024-03-04' },
  { region: 'DE', rep: 'Jonas', product: 'Gadget Mini', units: 3, unitPrice: 12.5, discountPct: 10, date: '2024-03-11' },
];

test('formats German amounts with dots and a euro sign', () => {
  assert.equal(formatMoney(1234.5, 'DE'), '1.234,50 €');
});

test('lists German sales with VAT and a subtotal', () => {
  const report = buildReport(germanSales);
  assert.equal(
    report,
    [
      'SALES REPORT',
      '',
      '== Germany ==',
      'Widget Pro              12       712,57 €',
      'Gadget Mini              3        40,16 €',
      'Subtotal DE: 752,73 €',
      '',
      'Rows: 2',
      'Large orders: 0',
      '',
    ].join('\n'),
  );
});

test('says so when there are no sales', () => {
  assert.equal(buildReport([]), 'SALES REPORT\n\nNo sales.\n');
});
