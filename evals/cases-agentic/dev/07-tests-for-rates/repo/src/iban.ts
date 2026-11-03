const IBAN_SHAPE = /^[A-Z]{2}\d{2}[A-Z0-9]{11,30}$/;

/** Whether the text is an IBAN with a correct check digit (ISO 13616, mod 97). Spaces are ignored. */
export function isValidIban(text: string): boolean {
  const iban = text.replaceAll(" ", "").toUpperCase();
  if (!IBAN_SHAPE.test(iban)) {
    return false;
  }
  const rearranged = iban.slice(4) + iban.slice(0, 4);
  let remainder = 0;
  for (const character of rearranged) {
    const value = parseInt(character, 36);
    remainder = Number(`${remainder}${value}`) % 97;
  }
  return remainder === 1;
}
