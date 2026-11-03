import { conflict, created, validationFailed } from '../response.js';

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const ROLES = ['owner', 'admin', 'member', 'viewer'];
const MAX_NAME_LENGTH = 80;

export function createUser(store, request) {
  const body = request.body ?? {};
  const messages = [];

  const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
  if (email === '') {
    messages.push('email is required');
  } else if (!EMAIL_PATTERN.test(email)) {
    messages.push('email is invalid');
  }

  const name = typeof body.name === 'string' ? body.name.trim() : '';
  if (name === '') {
    messages.push('name is required');
  } else if (name.length > MAX_NAME_LENGTH) {
    messages.push('name must be at most 80 characters');
  }

  const role = body.role === undefined ? 'member' : body.role;
  if (!ROLES.includes(role)) {
    messages.push('role is invalid');
  }

  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (store.findUserByEmail(email)) {
    return conflict('email already in use');
  }
  return created(store.addUser({ email, name, role }));
}
