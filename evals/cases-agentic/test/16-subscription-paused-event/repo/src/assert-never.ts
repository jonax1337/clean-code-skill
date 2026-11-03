/** Makes a `switch` over a union exhaustive: the compiler rejects the call while a case is still unhandled. */
export function assertNever(value: never): never {
  throw new Error(`Unhandled value: ${JSON.stringify(value)}`);
}
