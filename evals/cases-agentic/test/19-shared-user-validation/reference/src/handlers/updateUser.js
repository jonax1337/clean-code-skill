import { conflict, notFound, ok, validationFailed } from '../response.js';
import { checkEmail, checkName, checkRole, messagesOf } from '../userValidation.js';

export function updateUser(store, request) {
  const user = store.getUser(Number(request.params.id));
  if (!user) {
    return notFound('user not found');
  }

  const body = request.body ?? {};
  const results = {};
  if (body.email !== undefined) {
    results.email = checkEmail(body.email);
  }
  if (body.name !== undefined) {
    results.name = checkName(body.name);
  }
  if (body.role !== undefined) {
    results.role = checkRole(body.role);
  }

  const messages = messagesOf(Object.values(results));
  if (messages.length > 0) {
    return validationFailed(messages);
  }
  if (Object.keys(results).length === 0) {
    return validationFailed(['no fields to update']);
  }

  const changes = Object.fromEntries(Object.entries(results).map(([field, result]) => [field, result.value]));
  const owner = changes.email && store.findUserByEmail(changes.email);
  if (owner && owner.id !== user.id) {
    return conflict('email already in use');
  }
  return ok(store.updateUser(user.id, changes));
}
