export function parseSales(text) {
  return JSON.parse(text).map((record) => ({
    region: record.region,
    rep: record.rep,
    product: record.product,
    units: Number(record.units),
    unitPrice: Number(record.unitPrice),
    discountPct: Number(record.discountPct || 0),
    date: record.date,
  }));
}
