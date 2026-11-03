import { conflict, notFound, ok, validationFailed } from '../response.js';

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const ROLES = ['owner', 'admin', 'member', 'viewer'];
const MAX_NAME_LENGTH = 80;

export function updateUser(store, request) {
  const user = store.getUser(Number(request.params.id));
  if (!user) {
    return notFound('user not found');
  }

  const body = request.body ?? {};
  const messages = [];
  const changes = {};

  if (body.email !== undefined) {
    const email = typeof body.email === 'string' ? body.email.trim().toLowerCase() : '';
    if (email === '') {
      messages.push('email is required');
    } else if (!EMAIL_PATTERN.test(email)) {
      messages.push('email is invalid');
    } else {
      changes.email = email;
    }
  }

  if (body.name !== undefined) {
    const name = typeof body.name === 'string' ? body.name.trim() : '';
    if (name === '') {
      messages.push('name is required');
    } else if (name.length > MAX_NAME_LENGTH) {
      messages.push('name must be at most 80 characters');
    } else {
      changes.name = name;
    }
  }

  if (body.role !== undefined) {
    if (!ROLES.includes(body.role)) {
      messages.push('role is invalid');
    } else {
      changes.role = body.role;
    }
  }

  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (Object.keys(changes).length === 0) {
    return validationFailed(['no fields to update']);
  }

  const owner = changes.email && store.findUserByEmail(changes.email);
  if (owner && owner.id !== user.id) {
    return conflict('email already in use');
  }
  return ok(store.updateUser(user.id, changes));
}
