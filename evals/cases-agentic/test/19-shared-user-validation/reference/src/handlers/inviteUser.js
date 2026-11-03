import { conflict, created, validationFailed } from '../response.js';
import { INVITABLE_ROLES, checkEmail, checkName, checkRole, messagesOf } from '../userValidation.js';

export function inviteUser(store, request) {
  const body = request.body ?? {};

  const email = checkEmail(body.email);
  // The invitee fills in their name when they accept, so an empty name is fine here.
  const name = checkName(body.name, { optional: true });
  const role = body.role === undefined ? { message: 'role is required' } : checkRole(body.role, INVITABLE_ROLES);

  const messages = messagesOf([email, name, role]);
  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (store.findUserByEmail(email.value) || store.findInvitationByEmail(email.value)) {
    return conflict('email already in use');
  }
  return created(store.addInvitation({ email: email.value, name: name.value, role: role.value }));
}
