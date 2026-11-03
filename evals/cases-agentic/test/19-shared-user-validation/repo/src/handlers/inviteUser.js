import { conflict, created, validationFailed } from '../response.js';

const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const INVITABLE_ROLES = ['admin', 'member', 'viewer'];
const MAX_NAME_LENGTH = 80;

export function inviteUser(store, request) {
  const body = request.body ?? {};
  const messages = [];

  const email = typeof body.email === 'string' ? body.email.trim() : '';
  if (email === '') {
    messages.push('email is required');
  } else if (!EMAIL_PATTERN.test(email)) {
    messages.push('email is invalid');
  }

  // The invitee fills in their name when they accept, so an empty name is fine here.
  const name = typeof body.name === 'string' ? body.name.trim() : '';
  if (name.length > MAX_NAME_LENGTH) {
    messages.push('name must be at most 80 characters');
  }

  const role = body.role;
  if (role === undefined) {
    messages.push('role is required');
  } else if (!INVITABLE_ROLES.includes(role)) {
    messages.push('role is invalid');
  }

  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (store.findUserByEmail(email) || store.findInvitationByEmail(email)) {
    return conflict('email already in use');
  }
  return created(store.addInvitation({ email, name, role }));
}
