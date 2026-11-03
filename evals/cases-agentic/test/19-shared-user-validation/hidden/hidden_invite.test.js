import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inviteUser } from '../src/handlers/inviteUser.js';
import { ANN, LONG_NAME, MAX_NAME, storeWith, validationError } from './support.js';

function invite(body, store = storeWith()) {
  return inviteUser(store, { body });
}

test('a valid invitation is pending and keeps the trimmed name', () => {
  assert.deepEqual(invite({ email: ' bob@example.com ', name: ' Bob ', role: 'admin' }), {
    status: 201,
    body: { id: 1, email: 'bob@example.com', name: 'Bob', role: 'admin', status: 'pending' },
  });
});

test('the name is optional: missing, empty, blank and non-string names are stored as an empty string', () => {
  for (const name of [undefined, '', '   ', null, 7]) {
    const result = invite({ email: 'bob@example.com', role: 'member', name });
    assert.equal(result.status, 201, String(name));
    assert.equal(result.body.name, '', String(name));
  }
});

test('a name that is given is still limited to 80 characters', () => {
  assert.equal(invite({ email: 'bob@example.com', role: 'member', name: MAX_NAME }).status, 201);
  assert.deepEqual(
    invite({ email: 'bob@example.com', role: 'member', name: LONG_NAME }),
    validationError(['name must be at most 80 characters']),
  );
});

test('the role is required and has no default', () => {
  assert.deepEqual(invite({ email: 'bob@example.com' }), validationError(['role is required']));
});

test('owner cannot be invited, the other roles can', () => {
  assert.deepEqual(invite({ email: 'bob@example.com', role: 'owner' }), validationError(['role is invalid']));
  for (const role of ['admin', 'member', 'viewer']) {
    assert.equal(invite({ email: 'bob@example.com', role }).status, 201, role);
  }
});

test('an unknown or null role is invalid', () => {
  assert.deepEqual(invite({ email: 'bob@example.com', role: 'god' }), validationError(['role is invalid']));
  assert.deepEqual(invite({ email: 'bob@example.com', role: null }), validationError(['role is invalid']));
});

test('email problems use the same messages as everywhere else', () => {
  assert.deepEqual(invite({ role: 'member' }), validationError(['email is required']));
  assert.deepEqual(invite({ email: '  ', role: 'member' }), validationError(['email is required']));
  assert.deepEqual(invite({ email: 'bob@example', role: 'member' }), validationError(['email is invalid']));
});

test('messages come in the order email, name, role', () => {
  assert.deepEqual(
    invite({ email: 'nope', name: LONG_NAME }),
    validationError(['email is invalid', 'name must be at most 80 characters', 'role is required']),
  );
});

test('an email that belongs to a user or to a pending invitation answers 409', () => {
  const conflict = { status: 409, body: { error: 'conflict', message: 'email already in use' } };
  assert.deepEqual(invite({ email: 'ann@example.com', role: 'member' }, storeWith(ANN)), conflict);
  const store = storeWith();
  assert.equal(invite({ email: 'bob@example.com', role: 'member' }, store).status, 201);
  assert.deepEqual(invite({ email: 'bob@example.com', role: 'viewer' }, store), conflict);
});

test('nothing is stored when validation fails', () => {
  const store = storeWith();
  invite({ email: 'bob@example.com' }, store);
  assert.equal(store.findInvitationByEmail('bob@example.com'), undefined);
});
