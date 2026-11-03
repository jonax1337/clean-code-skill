import assert from 'node:assert/strict';
import { test } from 'node:test';
import { deleteUser } from '../src/handlers/deleteUser.js';
import { ann, storeWith } from './helpers.js';

test('deletes a user', () => {
  const store = storeWith(ann());
  assert.equal(deleteUser(store, { params: { id: '1' } }).status, 204);
  assert.equal(store.getUser(1), undefined);
});

test('refuses to delete the last owner', () => {
  const store = storeWith(ann({ role: 'owner' }));
  const result = deleteUser(store, { params: { id: '1' } });
  assert.equal(result.status, 409);
  assert.equal(result.body.message, 'cannot delete the last owner');
});
