import { parseContactsCsv, toContactsCsv } from "./csv.ts";
import { mergeContacts } from "./import.ts";

/** Merges an uploaded CSV into the stored address book and returns the new CSV. */
export function importCsv(storedCsv: string, uploadedCsv: string): string {
  const merged = mergeContacts(parseContactsCsv(storedCsv), parseContactsCsv(uploadedCsv));
  return toContactsCsv(merged);
}
