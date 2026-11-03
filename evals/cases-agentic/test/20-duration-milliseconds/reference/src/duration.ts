const MS_PER_UNIT: Record<string, number> = { s: 1000, m: 60_000, h: 3_600_000, d: 86_400_000 };

/** Parses a duration such as "30s", "5m", "2h" or "1d" and returns its length in milliseconds. */
export function parseDuration(text: string): number {
  const match = /^(\d+)([smhd])$/.exec(text.trim());
  if (match === null) {
    throw new Error(`Invalid duration: "${text}"`);
  }
  return Number(match[1]) * MS_PER_UNIT[match[2]];
}
