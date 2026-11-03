import { parseDuration } from "./duration.ts";

export interface RetryOptions {
  attempts: number;
  backoff: string;
}

export type Sleep = (ms: number) => Promise<void>;

const defaultSleep: Sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** Delay before retry number `attempt` (counting from 0): the base delay doubles with every attempt. */
export function backoffDelayMs(base: string, attempt: number): number {
  return parseDuration(base) * 1000 * 2 ** attempt;
}

export async function withRetry<T>(
  task: () => Promise<T>,
  options: RetryOptions,
  sleep: Sleep = defaultSleep,
): Promise<T> {
  let lastError: unknown;
  for (let attempt = 0; attempt < options.attempts; attempt++) {
    try {
      return await task();
    } catch (error) {
      lastError = error;
      if (attempt < options.attempts - 1) {
        await sleep(backoffDelayMs(options.backoff, attempt));
      }
    }
  }
  throw lastError;
}
