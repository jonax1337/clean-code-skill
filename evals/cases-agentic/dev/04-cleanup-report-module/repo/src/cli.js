import { readFileSync } from 'node:fs';
import { financeExport } from './export.js';
import { parseSales } from './sales.js';

const [file, month] = process.argv.slice(2);
if (!file) {
  console.error('usage: node src/cli.js <sales.json> [YYYY-MM]');
  process.exit(2);
}
process.stdout.write(financeExport(parseSales(readFileSync(file, 'utf8')), month));
