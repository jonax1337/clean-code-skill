import assert from 'node:assert/strict';
import { test } from 'node:test';
import { deleteUser } from '../src/handlers/deleteUser.js';
import { listUsers } from '../src/handlers/listUsers.js';
import { ANN, storeWith, validationError } from './support.js';

const BOB = { email: 'bob@example.com', name: 'Bob', role: 'owner' };

test('listUsers keeps its own paging rules and messages', () => {
  const store = storeWith(ANN, BOB);
  assert.deepEqual(listUsers(store, { query: { limit: '0' } }), validationError(['limit must be between 1 and 100']));
  assert.deepEqual(listUsers(store, { query: { limit: '1.5', offset: 'x' } }), validationError([
    'limit must be between 1 and 100',
    'offset must be 0 or greater',
  ]));
  assert.equal(listUsers(store, { query: { limit: '100' } }).status, 200);
  assert.deepEqual(listUsers(store, { query: { limit: '1', offset: '1' } }).body.users, [{ id: 2, ...BOB }]);
  assert.deepEqual(listUsers(store, { query: { q: '  ANN@' } }).body.users.map((user) => user.id), [1]);
});

test('deleteUser keeps its own rules', () => {
  const store = storeWith(ANN, BOB);
  assert.deepEqual(deleteUser(store, { params: { id: '2' } }), {
    status: 409,
    body: { error: 'conflict', message: 'cannot delete the last owner' },
  });
  assert.equal(deleteUser(store, { params: { id: '1' } }).status, 204);
  assert.equal(deleteUser(store, { params: { id: '1' } }).status, 404);
});
