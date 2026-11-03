const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
const MAX_NAME_LENGTH = 80;

export const ROLES = ['owner', 'admin', 'member', 'viewer'];
export const INVITABLE_ROLES = ROLES.filter((role) => role !== 'owner');

// Each check returns `{ value }` when the input is acceptable and `{ message }` when it is not.

export function checkEmail(input) {
  const email = typeof input === 'string' ? input.trim().toLowerCase() : '';
  if (email === '') {
    return { message: 'email is required' };
  }
  if (!EMAIL_PATTERN.test(email)) {
    return { message: 'email is invalid' };
  }
  return { value: email };
}

export function checkName(input, { optional = false } = {}) {
  const name = typeof input === 'string' ? input.trim() : '';
  if (name === '' && !optional) {
    return { message: 'name is required' };
  }
  if (name.length > MAX_NAME_LENGTH) {
    return { message: 'name must be at most 80 characters' };
  }
  return { value: name };
}

export function checkRole(input, allowedRoles = ROLES) {
  if (!allowedRoles.includes(input)) {
    return { message: 'role is invalid' };
  }
  return { value: input };
}

export function messagesOf(results) {
  return results.flatMap((result) => result.message ?? []);
}
