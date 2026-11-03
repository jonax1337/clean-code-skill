import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inviteUser } from '../src/handlers/inviteUser.js';
import { ann, storeWith } from './helpers.js';

test('creates a pending invitation', () => {
  const result = inviteUser(storeWith(), { body: { email: ' bob@example.com ', name: 'Bob', role: 'viewer' } });
  assert.equal(result.status, 201);
  assert.deepEqual(result.body, { id: 1, email: 'bob@example.com', name: 'Bob', role: 'viewer', status: 'pending' });
});

test('requires a role', () => {
  const result = inviteUser(storeWith(), { body: { email: 'bob@example.com' } });
  assert.deepEqual(result.body.messages, ['role is required']);
});

test('answers 409 when a user already has the email', () => {
  const result = inviteUser(storeWith(ann()), { body: { email: 'ann@example.com', role: 'member' } });
  assert.equal(result.status, 409);
});
