import { mergeContact } from "./merge.ts";
import { normalizeEmail } from "./normalize.ts";
import type { Contact } from "./types.ts";

/**
 * Adds the incoming contacts to the existing ones. A contact whose email is already present
 * is merged into that entry; everything else is appended in the order it arrives.
 */
export function mergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
  const result = [...existing];
  for (const contact of incoming) {
    const index = result.findIndex((entry) => normalizeEmail(entry.email) === normalizeEmail(contact.email));
    if (index === -1) {
      result.push(contact);
    } else {
      result[index] = mergeContact(result[index], contact);
    }
  }
  return result;
}
