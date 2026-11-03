export function invoiceTotalCents(invoice) {
  return invoice.lines.reduce((sum, line) => sum + line.quantity * line.unitPriceCents, 0);
}
