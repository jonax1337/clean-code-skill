import { parseDuration } from "./duration.ts";

const MIN_TTL_SECONDS = 5;
const MAX_TTL_SECONDS = 24 * 60 * 60;

/** Returns an error message for an unusable cache TTL, or null when the TTL is fine. */
export function validateTtl(ttl: string): string | null {
  let seconds: number;
  try {
    seconds = parseDuration(ttl);
  } catch {
    return `ttl "${ttl}" is not a duration`;
  }
  if (seconds < MIN_TTL_SECONDS) {
    return `ttl "${ttl}" is below the minimum of 5s`;
  }
  if (seconds > MAX_TTL_SECONDS) {
    return `ttl "${ttl}" exceeds the maximum of 1d`;
  }
  return null;
}
