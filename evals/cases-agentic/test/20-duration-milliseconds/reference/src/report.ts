import { parseDuration } from "./duration.ts";

export interface Settings {
  timeout: string;
  ttl: string;
}

export function describeSettings(settings: Settings): string {
  return `timeout ${parseDuration(settings.timeout) / 1000}s, ttl ${parseDuration(settings.ttl) / 1000}s`;
}
