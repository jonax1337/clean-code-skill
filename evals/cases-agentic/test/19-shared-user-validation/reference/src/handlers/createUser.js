import { conflict, created, validationFailed } from '../response.js';
import { checkEmail, checkName, checkRole, messagesOf } from '../userValidation.js';

export function createUser(store, request) {
  const body = request.body ?? {};

  const email = checkEmail(body.email);
  const name = checkName(body.name);
  const role = checkRole(body.role === undefined ? 'member' : body.role);

  const messages = messagesOf([email, name, role]);
  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (store.findUserByEmail(email.value)) {
    return conflict('email already in use');
  }
  return created(store.addUser({ email: email.value, name: name.value, role: role.value }));
}
