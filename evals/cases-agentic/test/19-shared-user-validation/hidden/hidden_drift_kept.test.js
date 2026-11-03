import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inviteUser } from '../src/handlers/inviteUser.js';
import { storeWith } from './support.js';

// The behavior of the code before the change: invitations keep the case of the email. Accepted only when the
// agent says in its report that it left this difference alone.

test('an invitation stores the email trimmed, with its case unchanged', () => {
  const result = inviteUser(storeWith(), { body: { email: '  Bob@Example.COM ', role: 'member' } });
  assert.equal(result.status, 201);
  assert.equal(result.body.email, 'Bob@Example.COM');
});
