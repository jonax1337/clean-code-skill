import assert from 'node:assert/strict';
import { test } from 'node:test';
import { listUsers } from '../src/handlers/listUsers.js';
import { ann, storeWith } from './helpers.js';

test('lists users and filters by name or email', () => {
  const store = storeWith(ann(), ann({ email: 'bob@example.com', name: 'Bob' }));
  assert.equal(listUsers(store, { query: {} }).body.total, 2);
  assert.deepEqual(listUsers(store, { query: { q: 'BOB' } }).body.users.map((user) => user.id), [2]);
});

test('rejects paging values out of range', () => {
  const result = listUsers(storeWith(), { query: { limit: '500', offset: '-1' } });
  assert.deepEqual(result.body.messages, ['limit must be between 1 and 100', 'offset must be 0 or greater']);
});
