import type { Contact } from "./types.ts";

/** Combines two records of the same person: the incoming record wins unless its field is empty. */
export function mergeContact(current: Contact, incoming: Contact): Contact {
  return {
    ...current,
    name: incoming.name !== "" ? incoming.name : current.name,
    phone: incoming.phone !== "" ? incoming.phone : current.phone,
    tags: [...new Set([...current.tags, ...incoming.tags])],
    updatedAt: Math.max(current.updatedAt, incoming.updatedAt),
  };
}
