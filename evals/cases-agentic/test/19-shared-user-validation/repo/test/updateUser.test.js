import assert from 'node:assert/strict';
import { test } from 'node:test';
import { updateUser } from '../src/handlers/updateUser.js';
import { ann, storeWith } from './helpers.js';

test('changes only the fields that are present', () => {
  const store = storeWith(ann());
  const result = updateUser(store, { params: { id: '1' }, body: { name: ' Anna Lee ' } });
  assert.equal(result.status, 200);
  assert.deepEqual(result.body, { id: 1, email: 'ann@example.com', name: 'Anna Lee', role: 'member' });
});

test('answers 404 for an unknown user', () => {
  const result = updateUser(storeWith(), { params: { id: '7' }, body: { name: 'Ann' } });
  assert.equal(result.status, 404);
});

test('rejects a present but invalid email', () => {
  const result = updateUser(storeWith(ann()), { params: { id: '1' }, body: { email: 'nope' } });
  assert.deepEqual(result.body.messages, ['email is invalid']);
});

test('answers 409 when the email belongs to another user', () => {
  const store = storeWith(ann(), ann({ email: 'bob@example.com', name: 'Bob' }));
  const result = updateUser(store, { params: { id: '2' }, body: { email: 'Ann@example.com' } });
  assert.equal(result.status, 409);
});
