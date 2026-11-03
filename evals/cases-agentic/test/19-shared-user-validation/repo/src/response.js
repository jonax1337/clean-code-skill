export function ok(body) {
  return { status: 200, body };
}

export function created(body) {
  return { status: 201, body };
}

export function noContent() {
  return { status: 204, body: null };
}

export function validationFailed(messages) {
  return { status: 400, body: { error: 'validation_failed', messages } };
}

export function notFound(message) {
  return { status: 404, body: { error: 'not_found', message } };
}

export function conflict(message) {
  return { status: 409, body: { error: 'conflict', message } };
}
