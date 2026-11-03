import { createStore } from '../src/store.js';

export function storeWith(...users) {
  const store = createStore();
  for (const user of users) {
    store.addUser(user);
  }
  return store;
}

export function ann(overrides = {}) {
  return { email: 'ann@example.com', name: 'Ann Lee', role: 'member', ...overrides };
}
