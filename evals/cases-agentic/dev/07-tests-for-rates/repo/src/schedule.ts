const SATURDAY = 6;
const SUNDAY = 0;

/** The next weekday after the given day, counted in UTC. Holidays are not considered. */
export function nextBusinessDay(from: Date): Date {
  const next = new Date(Date.UTC(from.getUTCFullYear(), from.getUTCMonth(), from.getUTCDate() + 1));
  while (next.getUTCDay() === SATURDAY || next.getUTCDay() === SUNDAY) {
    next.setUTCDate(next.getUTCDate() + 1);
  }
  return next;
}
