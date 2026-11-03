import assert from 'node:assert/strict';
import { test } from 'node:test';
import { INVITABLE_ROLES, checkEmail, checkName, checkRole, messagesOf } from '../src/userValidation.js';

test('an email is trimmed and lowercased', () => {
  assert.deepEqual(checkEmail('  Ann@Example.com '), { value: 'ann@example.com' });
});

test('a blank or non-string email is required, a malformed one is invalid', () => {
  assert.deepEqual(checkEmail('   '), { message: 'email is required' });
  assert.deepEqual(checkEmail(42), { message: 'email is required' });
  assert.deepEqual(checkEmail('ann@example'), { message: 'email is invalid' });
});

test('a name is trimmed, required and limited to 80 characters', () => {
  assert.deepEqual(checkName(' Ann '), { value: 'Ann' });
  assert.deepEqual(checkName(''), { message: 'name is required' });
  assert.deepEqual(checkName('a'.repeat(80)), { value: 'a'.repeat(80) });
  assert.deepEqual(checkName('a'.repeat(81)), { message: 'name must be at most 80 characters' });
});

test('an optional name may be empty but is still limited to 80 characters', () => {
  assert.deepEqual(checkName(undefined, { optional: true }), { value: '' });
  assert.deepEqual(checkName('a'.repeat(81), { optional: true }), {
    message: 'name must be at most 80 characters',
  });
});

test('roles are checked against the allowed list', () => {
  assert.deepEqual(checkRole('owner'), { value: 'owner' });
  assert.deepEqual(checkRole('god'), { message: 'role is invalid' });
  assert.deepEqual(checkRole('owner', INVITABLE_ROLES), { message: 'role is invalid' });
});

test('messagesOf keeps the messages in order and skips accepted values', () => {
  assert.deepEqual(messagesOf([{ value: 'a' }, { message: 'x' }, { message: 'y' }]), ['x', 'y']);
});
