import { createUser } from './handlers/createUser.js';
import { deleteUser } from './handlers/deleteUser.js';
import { inviteUser } from './handlers/inviteUser.js';
import { listUsers } from './handlers/listUsers.js';
import { updateUser } from './handlers/updateUser.js';

export const routes = [
  { method: 'GET', path: '/users', handler: listUsers },
  { method: 'POST', path: '/users', handler: createUser },
  { method: 'PATCH', path: '/users/:id', handler: updateUser },
  { method: 'DELETE', path: '/users/:id', handler: deleteUser },
  { method: 'POST', path: '/invitations', handler: inviteUser },
];
