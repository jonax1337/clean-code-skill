import { buildReport } from './report.js';

const EXPORT_HEADER = 'FINANCE-EXPORT v1';

export function financeExport(sales, month) {
  const body = buildReport(sales, { month });
  return `${EXPORT_HEADER}\n${body}`;
}
