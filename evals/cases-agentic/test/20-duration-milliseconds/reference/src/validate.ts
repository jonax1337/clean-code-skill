import { parseDuration } from "./duration.ts";

const MIN_TTL_MS = 5 * 1000;
const MAX_TTL_MS = 24 * 60 * 60 * 1000;

/** Returns an error message for an unusable cache TTL, or null when the TTL is fine. */
export function validateTtl(ttl: string): string | null {
  let ms: number;
  try {
    ms = parseDuration(ttl);
  } catch {
    return `ttl "${ttl}" is not a duration`;
  }
  if (ms < MIN_TTL_MS) {
    return `ttl "${ttl}" is below the minimum of 5s`;
  }
  if (ms > MAX_TTL_MS) {
    return `ttl "${ttl}" exceeds the maximum of 1d`;
  }
  return null;
}
