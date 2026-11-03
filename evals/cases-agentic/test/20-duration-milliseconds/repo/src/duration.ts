const SECONDS_PER_UNIT: Record<string, number> = { s: 1, m: 60, h: 3600, d: 86400 };

/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in seconds. */
export function parseDuration(text: string): number {
  const match = /^(\d+)([smhd])$/.exec(text.trim());
  if (match === null) {
    throw new Error(`Invalid duration: "${text}"`);
  }
  return Number(match[1]) * SECONDS_PER_UNIT[match[2]];
}
