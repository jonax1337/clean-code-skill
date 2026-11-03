import assert from 'node:assert/strict';
import { test } from 'node:test';
import { financeExport } from '../src/export.js';

test('the export starts with the format header', () => {
  const exported = financeExport([], '2024-03');
  assert.equal(exported, 'FINANCE-EXPORT v1\nSALES REPORT 2024-03\n\nNo sales.\n');
});
