/** Formats an amount of minor units for display, for example 123456 with 2 minor units as "1,234.56". */
export function formatMinor(amountMinor: number, minorUnits: number): string {
  const sign = amountMinor < 0 ? "-" : "";
  const digits = String(Math.abs(amountMinor)).padStart(minorUnits + 1, "0");
  const whole = digits.slice(0, digits.length - minorUnits);
  const fraction = digits.slice(digits.length - minorUnits);
  const grouped = whole.replace(/\B(?=(\d{3})+$)/g, ",");
  return minorUnits === 0 ? `${sign}${grouped}` : `${sign}${grouped}.${fraction}`;
}
