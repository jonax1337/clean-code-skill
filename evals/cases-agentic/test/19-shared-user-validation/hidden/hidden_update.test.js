import assert from 'node:assert/strict';
import { test } from 'node:test';
import { updateUser } from '../src/handlers/updateUser.js';
import { ANN, LONG_NAME, MAX_NAME, storeWith, validationError } from './support.js';

function update(body, store = storeWith(ANN)) {
  return updateUser(store, { params: { id: '1' }, body });
}

test('a single field can be changed on its own', () => {
  assert.deepEqual(update({ role: 'viewer' }), {
    status: 200,
    body: { id: 1, ...ANN, role: 'viewer' },
  });
  assert.deepEqual(update({ name: ' Anna ' }).body, { id: 1, ...ANN, name: 'Anna' });
});

test('an email is trimmed and lowercased', () => {
  assert.equal(update({ email: '  New@Example.COM ' }).body.email, 'new@example.com');
});

test('all three fields can be changed together', () => {
  assert.deepEqual(update({ email: 'a@b.io', name: 'A', role: 'owner' }).body, {
    id: 1,
    email: 'a@b.io',
    name: 'A',
    role: 'owner',
  });
});

test('a body without any field is rejected with one message', () => {
  assert.deepEqual(update({}), validationError(['no fields to update']));
  assert.deepEqual(update(undefined), validationError(['no fields to update']));
});

test('a field that is present must be valid, even when it is empty', () => {
  assert.deepEqual(update({ email: '' }), validationError(['email is required']));
  assert.deepEqual(update({ name: '   ' }), validationError(['name is required']));
  assert.deepEqual(update({ name: null }), validationError(['name is required']));
  assert.deepEqual(update({ role: null }), validationError(['role is invalid']));
  assert.deepEqual(update({ email: 'nope' }), validationError(['email is invalid']));
  assert.deepEqual(update({ name: LONG_NAME }), validationError(['name must be at most 80 characters']));
  assert.equal(update({ name: MAX_NAME }).status, 200);
});

test('only the fields that are present are reported, in the order email, name, role', () => {
  assert.deepEqual(
    update({ role: 'god', email: 'nope' }),
    validationError(['email is invalid', 'role is invalid']),
  );
});

test('an invalid field prevents the valid ones from being applied', () => {
  const store = storeWith(ANN);
  update({ name: 'Anna', role: 'god' }, store);
  assert.deepEqual(store.getUser(1), { id: 1, ...ANN });
});

test('an unknown user answers 404 before the body is looked at', () => {
  const expected = { status: 404, body: { error: 'not_found', message: 'user not found' } };
  assert.deepEqual(updateUser(storeWith(), { params: { id: '9' }, body: {} }), expected);
  assert.deepEqual(updateUser(storeWith(), { params: { id: '9' }, body: { role: 'god' } }), expected);
});

test('the email of another user answers 409, the own email does not', () => {
  const store = storeWith(ANN, { email: 'bob@example.com', name: 'Bob', role: 'member' });
  assert.deepEqual(updateUser(store, { params: { id: '2' }, body: { email: 'ANN@example.com' } }), {
    status: 409,
    body: { error: 'conflict', message: 'email already in use' },
  });
  assert.equal(updateUser(store, { params: { id: '1' }, body: { email: ' Ann@Example.com' } }).status, 200);
});
