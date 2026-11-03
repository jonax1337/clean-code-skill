import { parseDuration } from "./duration.ts";

/** Response headers for a rate-limited request; `Retry-After` is specified in whole seconds. */
export function rateLimitHeaders(wait: string): Record<string, string> {
  return { "Retry-After": String(parseDuration(wait)) };
}
