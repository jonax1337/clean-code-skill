import assert from 'node:assert/strict';
import { test } from 'node:test';
import { topDeals } from '../src/digest.js';
import { financeExport } from '../src/export.js';
import * as report from '../src/report.js';
import { parseSales } from '../src/sales.js';

const sales = parseSales(
  JSON.stringify([
    { region: 'DE', rep: 'Anke', product: 'Widget Pro', units: 12, unitPrice: 49.9, date: '2024-03-04' },
    { region: 'FR', rep: 'Claire', product: 'Widget Pro', units: 30, unitPrice: 51, date: '2024-03-12' },
    {
      region: 'UK',
      rep: 'Oliver',
      product: 'Premium Support Contract',
      units: 1,
      unitPrice: 9800,
      date: '2024-04-02',
    },
  ]),
);

test('report.js still exports exactly buildReport and formatMoney', () => {
  assert.deepEqual(Object.keys(report).sort(), ['buildReport', 'formatMoney']);
  assert.equal(typeof report.buildReport, 'function');
  assert.equal(typeof report.formatMoney, 'function');
});

test('the finance export still wraps the report', () => {
  assert.equal(
    financeExport(sales, '2024-03'),
    [
      'FINANCE-EXPORT v1',
      'SALES REPORT 2024-03',
      '',
      '== Germany ==',
      'Widget Pro              12       712,57 €',
      'Subtotal DE: 712,57 €',
      '',
      '== France ==',
      'Widget Pro              30     1 836,00 €',
      'Subtotal FR: 1 836,00 €',
      '',
      'Rows: 2',
      'Large orders: 0',
      '',
    ].join('\n'),
  );
});

test('the digest still formats the top deals', () => {
  assert.deepEqual(topDeals(sales), ['Oliver: £9,800.00', 'Claire: 1 530,00 €', 'Anke: 598,80 €']);
});
