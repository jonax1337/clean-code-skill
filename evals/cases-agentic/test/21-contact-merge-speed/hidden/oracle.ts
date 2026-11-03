// The merge exactly as it behaved before the speed-up.
import { mergeContact } from "../src/merge.ts";
import { normalizeEmail } from "../src/normalize.ts";
import type { Contact } from "../src/types.ts";

export function referenceMergeContacts(existing: Contact[], incoming: Contact[]): Contact[] {
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

/** Small deterministic random generator so failures are reproducible. */
export function randomSource(seed: number): () => number {
  let state = seed;
  return () => {
    state = (state * 1664525 + 1013904223) % 4294967296;
    return state / 4294967296;
  };
}

export function randomContacts(random: () => number, count: number, emailPool: number, idPrefix: string): Contact[] {
  const decorate = [(s: string) => s, (s: string) => s.toUpperCase(), (s: string) => ` ${s} `, (s: string) => `${s} `];
  return Array.from({ length: count }, (_, i) => {
    const email = `user${Math.floor(random() * emailPool)}@example.com`;
    return {
      id: `${idPrefix}${i}`,
      email: decorate[Math.floor(random() * decorate.length)](email),
      name: random() < 0.3 ? "" : `Name ${idPrefix}${i}`,
      phone: random() < 0.5 ? "" : `555-${i}`,
      tags: [`t${Math.floor(random() * 4)}`, `t${Math.floor(random() * 4)}`],
      updatedAt: Math.floor(random() * 1000),
    };
  });
}
