import assert from 'node:assert/strict';
import { test } from 'node:test';
import { topDeals } from '../src/digest.js';

test('lists the biggest deals first', () => {
  const sales = [
    { region: 'DE', rep: 'Anke', product: 'A', units: 1, unitPrice: 100, date: '2024-03-01' },
    { region: 'UK', rep: 'Oliver', product: 'B', units: 2, unitPrice: 1500.5, date: '2024-03-02' },
  ];
  assert.deepEqual(topDeals(sales, 2), ['Oliver: £3,001.00', 'Anke: 100,00 €']);
});
