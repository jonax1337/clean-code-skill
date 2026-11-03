// Sales report. Used by the finance export (export.js) and the weekly digest (digest.js).
// The layout is parsed by the finance team's import, so do not move columns around.
// TODO: US region once the tax rules are clear

export function formatMoney(amount, region) {
  let sign = '';
  if (amount < 0) {
    sign = '-';
    amount = -amount;
  }
  const fixed = amount.toFixed(2);
  const ip = fixed.slice(0, fixed.length - 3);
  const cents = fixed.slice(-2);
  const groups = [];
  for (let i = ip.length; i > 0; i -= 3) {
    groups.unshift(ip.slice(Math.max(0, i - 3), i));
  }
  if (region === 'DE') {
    return sign + groups.join('.') + ',' + cents + ' €';
  }
  if (region === 'FR') {
    return sign + groups.join(' ') + ',' + cents + ' €';
  }
  if (region === 'UK') {
    return sign + '£' + groups.join(',') + '.' + cents;
  }
  throw new Error('unknown region: ' + region);
}

export function buildReport(sales, options) {
  options = options || {};
  if (options.format && options.format !== 'text') {
    throw new Error('unsupported format: ' + options.format);
  }
  if (options.month && !/^\d{4}-\d{2}$/.test(options.month)) {
    throw new Error('bad month: ' + options.month);
  }
  const res = [];
  res.push(options.month ? 'SALES REPORT ' + options.month : 'SALES REPORT');
  res.push('');
  let data = sales.slice();
  // data = data.filter((s) => s.status !== 'void');
  if (options.month) {
    data = data.filter((s) => s.date.slice(0, 7) === options.month);
  }
  data.sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : 0));
  let total = 0;
  let big = 0;

  /*
  const quarter = options.quarter;
  if (quarter) {
    data = data.filter((s) => Math.ceil(Number(s.date.slice(5, 7)) / 3) === quarter);
  }
  */

  if (options.format === 'legacy') {
    // old finance import, replaced in 2021
    for (const s of data) {
      res.push([s.region, s.rep, s.product, s.units, s.unitPrice].join(';'));
    }
    return res.join('\r\n');
  }

  // Germany
  const de = data.filter((s) => s.region === 'DE' && s.units > 0);
  if (de.length > 0) {
    res.push('== Germany ==');
    let sub = 0;
    for (let i = 0; i < de.length; i++) {
      const s = de[i];
      let x = s.units * s.unitPrice;
      if (s.discountPct) {
        x = x - (x * s.discountPct) / 100;
      }
      if (s.units >= 100) {
        x = x * 0.95;
      }
      x = Math.round(x * 100) / 100;
      const tax = Math.round(x * 0.19 * 100) / 100;
      const amount = Math.round((x + tax) * 100) / 100;
      const fixed = amount.toFixed(2);
      const ip = fixed.split('.')[0];
      let grouped = '';
      for (let k = 0; k < ip.length; k++) {
        if (k > 0 && (ip.length - k) % 3 === 0) {
          grouped += '.';
        }
        grouped += ip[k];
      }
      const money = grouped + ',' + fixed.split('.')[1] + ' €';
      let name = s.product;
      if (name.length > 20) {
        name = name.slice(0, 19) + '…';
      }
      let line = name;
      while (line.length < 20) {
        line += ' ';
      }
      line += ' ' + String(s.units).padStart(5);
      line += ' ' + money.padStart(14);
      if (amount >= 10000) {
        line += ' *';
        big++;
      }
      res.push(line);
      sub += amount;
      total++;
    }
    res.push('Subtotal DE: ' + formatMoney(sub, 'DE'));
    res.push('');
  }

  // France
  const fr = data.filter((s) => s.region === 'FR' && s.units > 0);
  if (fr.length > 0) {
    res.push('== France ==');
    let sub = 0;
    for (const s of fr) {
      const d = s.discountPct || 0;
      let n = s.units * s.unitPrice;
      n = n - (n * d) / 100;
      if (s.units >= 100) n *= 0.95;
      n = Math.round(n * 100) / 100;
      const t = Math.round(n * 0.2 * 100) / 100;
      const a = Math.round((n + t) * 100) / 100;
      const parts = a.toFixed(2).split('.');
      const money = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ' ') + ',' + parts[1] + ' €';
      const nm = s.product.length > 20 ? s.product.substring(0, 19) + '…' : s.product;
      const u = String(s.units);
      let line = nm.padEnd(20) + ' ' + ' '.repeat(Math.max(0, 5 - u.length)) + u + ' ' + money.padStart(14);
      if (a >= 10000) {
        line = line + ' *';
        big += 1;
      }
      res.push(line);
      sub += a;
      total += 1;
    }
    res.push('Subtotal FR: ' + formatMoney(sub, 'FR'));
    res.push('');
  }

  // United Kingdom
  const uk = data.filter((s) => s.units > 0 && s.region === 'UK');
  if (uk.length > 0) {
    res.push('== United Kingdom ==');
    let sub = 0;
    uk.forEach((s) => {
      let v = s.units * s.unitPrice;
      if (s.discountPct) v = v - (v * s.discountPct) / 100;
      if (s.units >= 100) {
        v = v * 0.95;
      }
      v = Math.round(v * 100) / 100;
      const vt = Math.round(v * 0.2 * 100) / 100;
      const g = Math.round((v + vt) * 100) / 100;
      const digits = g.toFixed(2).split('.');
      const chunks = [];
      const rev = digits[0].split('').reverse();
      for (let j = 0; j < rev.length; j += 3) {
        chunks.unshift(rev.slice(j, j + 3).reverse().join(''));
      }
      const money = '£' + chunks.join(',') + '.' + digits[1];
      const label = s.product.length <= 20 ? s.product : s.product.slice(0, 19) + '…';
      let line = label.padEnd(20);
      line += ' ' + String(s.units).padStart(5);
      line += ' ' + money.padStart(14);
      if (10000 <= g) {
        line += ' *';
        big++;
      }
      res.push(line);
      sub += g;
      total++;
    });
    res.push('Subtotal UK: ' + formatMoney(sub, 'UK'));
    res.push('');
  }

  if (total === 0) {
    res.push('No sales.');
  } else {
    res.push('Rows: ' + total);
    res.push('Large orders: ' + big);
  }
  return res.join('\n') + '\n';
}
