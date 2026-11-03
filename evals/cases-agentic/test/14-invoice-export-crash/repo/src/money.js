/** Formats integer cents as a decimal amount, for example 1250 as "12.50". */
export function formatCents(cents) {
  return (cents / 100).toFixed(2);
}
