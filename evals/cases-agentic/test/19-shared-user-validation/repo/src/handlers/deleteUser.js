import { conflict, noContent, notFound } from '../response.js';

export function deleteUser(store, request) {
  const user = store.getUser(Number(request.params.id));
  if (!user) {
    return notFound('user not found');
  }

  const owners = store.listUsers().filter((candidate) => candidate.role === 'owner');
  if (user.role === 'owner' && owners.length === 1) {
    return conflict('cannot delete the last owner');
  }
  store.removeUser(user.id);
  return noContent();
}
