import type { Contact } from "./types.ts";

export interface Summary {
  total: number;
  withPhone: number;
  tagCounts: Record<string, number>;
}

export function summarize(contacts: Contact[]): Summary {
  const tagCounts: Record<string, number> = {};
  let withPhone = 0;
  for (const contact of contacts) {
    if (contact.phone !== "") {
      withPhone++;
    }
    for (const tag of contact.tags) {
      tagCounts[tag] = (tagCounts[tag] ?? 0) + 1;
    }
  }
  return { total: contacts.length, withPhone, tagCounts };
}
