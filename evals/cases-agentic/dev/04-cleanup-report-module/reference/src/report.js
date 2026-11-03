// Sales report. Used by the finance export (export.js) and the weekly digest (digest.js).
// The layout is parsed by the finance team's import, so do not move columns around.

const NAME_WIDTH = 20;
const UNITS_WIDTH = 5;
const MONEY_WIDTH = 14;
const ELLIPSIS = '…';
const LARGE_ORDER_MARK = ' *';
const LARGE_ORDER_AMOUNT = 10000;
const BULK_UNITS = 100;
const BULK_FACTOR = 0.95;
const MONTH_FORMAT = /^\d{4}-\d{2}$/;

const REGIONS = {
  DE: { label: 'Germany', vatRate: 0.19 },
  FR: { label: 'France', vatRate: 0.2 },
  UK: { label: 'United Kingdom', vatRate: 0.2 },
};

const MONEY_STYLES = {
  DE: { prefix: '', suffix: ' €', group: '.', decimal: ',' },
  FR: { prefix: '', suffix: ' €', group: ' ', decimal: ',' },
  UK: { prefix: '£', suffix: '', group: ',', decimal: '.' },
};

export function formatMoney(amount, region) {
  const style = MONEY_STYLES[region];
  if (!style) {
    throw new Error('unknown region: ' + region);
  }
  const sign = amount < 0 ? '-' : '';
  const [whole, cents] = Math.abs(amount).toFixed(2).split('.');
  const grouped = whole.replace(/\B(?=(\d{3})+(?!\d))/g, style.group);
  return sign + style.prefix + grouped + style.decimal + cents + style.suffix;
}

export function buildReport(sales, options) {
  options = options || {};
  assertSupported(options);

  const title = options.month ? 'SALES REPORT ' + options.month : 'SALES REPORT';
  const lines = [title, ''];
  const counts = { rows: 0, large: 0 };
  const selected = selectSales(sales, options.month);
  for (const [region, { label, vatRate }] of Object.entries(REGIONS)) {
    const regionSales = selected.filter((sale) => sale.region === region && sale.units > 0);
    if (regionSales.length > 0) {
      lines.push(...renderRegion(regionSales, region, label, vatRate, counts), '');
    }
  }

  if (counts.rows === 0) {
    lines.push('No sales.');
  } else {
    lines.push('Rows: ' + counts.rows, 'Large orders: ' + counts.large);
  }
  return lines.join('\n') + '\n';
}

function renderRegion(regionSales, region, label, vatRate, counts) {
  const lines = [`== ${label} ==`];
  let subtotal = 0;
  for (const sale of regionSales) {
    const gross = grossAmount(sale, vatRate);
    lines.push(formatRow(sale, gross, region));
    subtotal += gross;
    counts.rows++;
    if (gross >= LARGE_ORDER_AMOUNT) {
      counts.large++;
    }
  }
  lines.push(`Subtotal ${region}: ${formatMoney(subtotal, region)}`);
  return lines;
}

function assertSupported(options) {
  if (options.format && options.format !== 'text') {
    throw new Error('unsupported format: ' + options.format);
  }
  if (options.month && !MONTH_FORMAT.test(options.month)) {
    throw new Error('bad month: ' + options.month);
  }
}

function selectSales(sales, month) {
  const inMonth = month ? sales.filter((sale) => sale.date.slice(0, 7) === month) : sales.slice();
  return inMonth.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
}

function roundToCents(value) {
  return Math.round(value * 100) / 100;
}

function grossAmount(sale, vatRate) {
  let net = sale.units * sale.unitPrice;
  if (sale.discountPct) {
    net = net - (net * sale.discountPct) / 100;
  }
  if (sale.units >= BULK_UNITS) {
    net = net * BULK_FACTOR;
  }
  net = roundToCents(net);
  const vat = roundToCents(net * vatRate);
  return roundToCents(net + vat);
}

function formatRow(sale, gross, region) {
  const name = sale.product.length > NAME_WIDTH ? sale.product.slice(0, NAME_WIDTH - 1) + ELLIPSIS : sale.product;
  const columns = [
    name.padEnd(NAME_WIDTH),
    String(sale.units).padStart(UNITS_WIDTH),
    formatMoney(gross, region).padStart(MONEY_WIDTH),
  ];
  const row = columns.join(' ');
  return gross >= LARGE_ORDER_AMOUNT ? row + LARGE_ORDER_MARK : row;
}
