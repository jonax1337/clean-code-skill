import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createUser } from '../src/handlers/createUser.js';
import { ann, storeWith } from './helpers.js';

test('creates a user with a trimmed, lowercase email and the default role', () => {
  const store = storeWith();
  const result = createUser(store, { body: { email: '  Ann@Example.com ', name: ' Ann Lee ' } });
  assert.equal(result.status, 201);
  assert.deepEqual(result.body, { id: 1, email: 'ann@example.com', name: 'Ann Lee', role: 'member' });
});

test('rejects a missing email', () => {
  const result = createUser(storeWith(), { body: { name: 'Ann Lee' } });
  assert.equal(result.status, 400);
  assert.deepEqual(result.body.messages, ['email is required']);
});

test('rejects an unknown role', () => {
  const result = createUser(storeWith(), { body: { email: 'ann@example.com', name: 'Ann', role: 'god' } });
  assert.deepEqual(result.body.messages, ['role is invalid']);
});

test('answers 409 when the email is taken', () => {
  const result = createUser(storeWith(ann()), { body: { email: 'ANN@example.com', name: 'Other Ann' } });
  assert.equal(result.status, 409);
  assert.equal(result.body.message, 'email already in use');
});
