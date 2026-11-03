function formatCell(value) {
  const text = String(value);
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function toCsv(rows) {
  return rows.map((row) => `${row.map(formatCell).join(",")}\n`).join("");
}
