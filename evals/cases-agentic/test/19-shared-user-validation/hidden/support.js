import { createStore } from '../src/store.js';

export function storeWith(...users) {
  const store = createStore();
  for (const user of users) {
    store.addUser(user);
  }
  return store;
}

export const ANN = { email: 'ann@example.com', name: 'Ann Lee', role: 'member' };

export function validationError(messages) {
  return { status: 400, body: { error: 'validation_failed', messages } };
}

export const LONG_NAME = 'n'.repeat(81);
export const MAX_NAME = 'n'.repeat(80);
