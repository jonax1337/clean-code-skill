import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inviteUser } from '../src/handlers/inviteUser.js';
import { ANN, storeWith } from './support.js';

// docs/api.md: email addresses are stored trimmed and in lowercase, for users and for invitations.

test('an invitation stores the email trimmed and in lowercase', () => {
  const result = inviteUser(storeWith(), { body: { email: '  Bob@Example.COM ', role: 'member' } });
  assert.equal(result.status, 201);
  assert.equal(result.body.email, 'bob@example.com');
});

test('an invitation for an existing user is found whatever the case of the email', () => {
  const result = inviteUser(storeWith(ANN), { body: { email: 'ANN@Example.com', role: 'member' } });
  assert.equal(result.status, 409);
});
