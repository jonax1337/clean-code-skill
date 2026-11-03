import assert from 'node:assert/strict';
import { test } from 'node:test';
import { createUser } from '../src/handlers/createUser.js';
import { ANN, LONG_NAME, MAX_NAME, storeWith, validationError } from './support.js';

function create(body, store = storeWith()) {
  return createUser(store, { body });
}

test('a valid request stores a trimmed, lowercase email and a trimmed name', () => {
  assert.deepEqual(create({ email: '  Bob@Example.COM ', name: '  Bob Ray ', role: 'admin' }), {
    status: 201,
    body: { id: 1, email: 'bob@example.com', name: 'Bob Ray', role: 'admin' },
  });
});

test('the role defaults to member', () => {
  assert.equal(create({ email: 'bob@example.com', name: 'Bob' }).body.role, 'member');
});

test('every role of the docs is accepted', () => {
  for (const role of ['owner', 'admin', 'member', 'viewer']) {
    assert.equal(create({ email: 'bob@example.com', name: 'Bob', role }).status, 201, role);
  }
});

test('a name of exactly 80 characters is accepted', () => {
  assert.equal(create({ email: 'bob@example.com', name: MAX_NAME }).status, 201);
});

test('all failing fields report their message, in the order email, name, role', () => {
  assert.deepEqual(create({}), validationError(['email is required', 'name is required']));
  assert.deepEqual(
    create({ email: 'nope', name: LONG_NAME, role: 'god' }),
    validationError(['email is invalid', 'name must be at most 80 characters', 'role is invalid']),
  );
});

test('blank and non-string values count as missing', () => {
  assert.deepEqual(
    create({ email: '   ', name: '\t' }),
    validationError(['email is required', 'name is required']),
  );
  assert.deepEqual(
    create({ email: 42, name: ['Bob'] }),
    validationError(['email is required', 'name is required']),
  );
});

test('malformed emails are invalid', () => {
  for (const email of ['bob', 'bob@example', '@example.com', 'bob@.com', 'b ob@example.com', 'bob@exa mple.com']) {
    assert.deepEqual(create({ email, name: 'Bob' }), validationError(['email is invalid']), email);
  }
});

test('a null or unknown role is invalid, only a missing role defaults', () => {
  assert.deepEqual(create({ email: 'bob@example.com', name: 'Bob', role: null }), validationError(['role is invalid']));
  assert.deepEqual(create({ email: 'bob@example.com', name: 'Bob', role: 'Admin' }), validationError(['role is invalid']));
});

test('a taken email answers 409, whatever its case', () => {
  assert.deepEqual(create({ email: ' ANN@example.com', name: 'Other' }, storeWith(ANN)), {
    status: 409,
    body: { error: 'conflict', message: 'email already in use' },
  });
});

test('nothing is stored when validation fails', () => {
  const store = storeWith();
  create({ email: 'bob@example.com' }, store);
  assert.deepEqual(store.listUsers(), []);
});
