import { ok, validationFailed } from '../response.js';

const DEFAULT_LIMIT = 25;
const MAX_LIMIT = 100;

export function listUsers(store, request) {
  const query = request.query ?? {};
  const limit = query.limit === undefined ? DEFAULT_LIMIT : Number(query.limit);
  const offset = query.offset === undefined ? 0 : Number(query.offset);

  const messages = [];
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_LIMIT) {
    messages.push('limit must be between 1 and 100');
  }
  if (!Number.isInteger(offset) || offset < 0) {
    messages.push('offset must be 0 or greater');
  }
  if (messages.length > 0) {
    return validationFailed(messages);
  }

  const needle = (query.q ?? '').trim().toLowerCase();
  const matching = store
    .listUsers()
    .filter((user) => user.name.toLowerCase().includes(needle) || user.email.includes(needle));
  return ok({ users: matching.slice(offset, offset + limit), total: matching.length });
}
